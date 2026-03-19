import argparse
import os
import sys
import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import DataLoader
import numpy as np
import time
import csv
from huggingface_hub import hf_hub_download
import safetensors.torch

# Add Large-Time-Series-Model to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Large-Time-Series-Model"))

from exp.exp_forecast import Exp_Forecast
from models import Timer
from utils.tools import EarlyStopping, adjust_learning_rate
from dataset import SectorDataset

class Exp_Sector_Finetune(Exp_Forecast):
    def _build_model(self):
        # Load the model structure
        model = Timer.Model(self.args).float()
        
        # Download weights if not present
        if self.args.pretrained_weight_path:
             weight_path = self.args.pretrained_weight_path
             # Determine loader based on extension
             if weight_path.endswith(".safetensors"):
                 state_dict = safetensors.torch.load_file(weight_path)
             else:
                 state_dict = torch.load(weight_path, map_location='cpu')
        else:
             print("Downloading Timer-base-84m weights...")
             # Try safetensors first
             try:
                 weight_path = hf_hub_download(repo_id="thuml/timer-base-84m", filename="model.safetensors")
                 state_dict = safetensors.torch.load_file(weight_path)
             except Exception:
                 # Fallback
                 weight_path = hf_hub_download(repo_id="thuml/timer-base-84m", filename="pytorch_model.bin")
                 state_dict = torch.load(weight_path, map_location='cpu')
        
        print(f"Loading weights from {weight_path}")
        # Timer weights might have prefix or not. Timer.py handles some, but let's be robust.
        # Adjusted for standard HuggingFace keys vs internal Timer keys
        # The Timer repo models often use 'backbone.' prefix.
        
        msg = model.load_state_dict(state_dict, strict=False)
        print("Load result:", msg)

        # Freeze early layers
        # Timer has encoder/decoder (Timer is decoder-only, so 'decoder' in code)
        # model.backbone.decoder.attn_layers is ModuleList
        
        layers_to_train = self.args.train_layers_last
        total_layers = len(model.backbone.decoder.attn_layers)
        
        print(f"Freezing first {total_layers - layers_to_train} layers, training last {layers_to_train}...")
        
        for i, layer in enumerate(model.backbone.decoder.attn_layers):
            if i < total_layers - layers_to_train:
                for param in layer.parameters():
                    param.requires_grad = False
            else:
                for param in layer.parameters():
                    param.requires_grad = True
        
        # Also maybe freeze embeddings?
        # for param in model.backbone.patch_embedding.parameters():
        #     param.requires_grad = False
            
        if self.args.use_gpu:
            model = model.cuda()
        return model

    def _get_data(self, flag):
        args = self.args
        data_set = SectorDataset(
            root_path=args.root_path,
            data_path=args.data_path,
            flag=flag,
            size=[args.seq_len, args.label_len, args.pred_len],
            features=args.features,
            target=args.target,
            timeenc=0, # Simple for now
            freq=args.freq
        )
        print(f"Loaded {flag} set: {len(data_set)} samples")
        
        shuffle_flag = True if flag == 'train' else False
        drop_last = True
        batch_size = args.batch_size
        
        data_loader = DataLoader(
            data_set,
            batch_size=batch_size,
            shuffle=shuffle_flag,
            num_workers=args.num_workers,
            drop_last=drop_last)
            
        return data_set, data_loader

    def finetune(self, setting):
        finetune_data, finetune_loader = self._get_data(flag='train')
        vali_data, vali_loader = self._get_data(flag='val')
        
        path = os.path.join(self.args.checkpoints, setting)
        if not os.path.exists(path):
            os.makedirs(path)

        train_steps = len(finetune_loader)
        early_stopping = EarlyStopping(patience=self.args.early_stop_patience, verbose=True)
        model_optim = self._select_optimizer()
        criterion = self._select_criterion()

        # CSV Logging
        log_path = os.path.join(path, "metrics.csv")
        with open(log_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["epoch", "train_loss", "vali_loss", "mse"])

        for epoch in range(self.args.train_epochs):
            iter_count = 0
            train_loss = []
            
            self.model.train()
            epoch_time = time.time()
            
            for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(finetune_loader):
                iter_count += 1
                model_optim.zero_grad()
                
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.float().to(self.device)
                batch_x_mark = batch_x_mark.float().to(self.device)
                batch_y_mark = batch_y_mark.float().to(self.device)
                # Apply augmentation if enabled
                if self.args.augment:
                    noise = torch.randn_like(batch_x) * 0.01
                    batch_x = batch_x + noise

                # Decoder input
                dec_inp = torch.zeros_like(batch_y[:, -self.args.pred_len:, :]).float()
                dec_inp = torch.cat([batch_y[:, :self.args.label_len, :], dec_inp], dim=1).float().to(self.device)

                outputs = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)

                # Loss
                f_dim = -1 if self.args.features == 'MS' else 0
                outputs = outputs[:, -self.args.pred_len:, f_dim:]
                batch_y_target = batch_y[:, -self.args.pred_len:, f_dim:].to(self.device)
                
                loss = criterion(outputs, batch_y_target)
                loss = loss / self.args.accum_iter
                train_loss.append(loss.item() * self.args.accum_iter)
                
                loss.backward()
                
                if (i + 1) % self.args.accum_iter == 0:
                    model_optim.step()
                    model_optim.zero_grad()
                
                if (i + 1) % 100 == 0:
                     print(f"\titer: {i+1}, epoch: {epoch+1} | loss: {loss.item() * self.args.accum_iter:.7f}")

            print(f"Epoch: {epoch+1} cost time: {time.time() - epoch_time}")
            train_loss_avg = np.average(train_loss)
            
            vali_loss = self.vali(vali_data, vali_loader, criterion)
            
            # MSE Eval (same as vali loss if criterion is MSE)
            mse = vali_loss 
            
            print(f"Epoch: {epoch+1}, Train Loss: {train_loss_avg:.7f} Vali Loss: {vali_loss:.7f} MSE: {mse:.7f}")
            
            # Log to CSV
            with open(log_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([epoch+1, train_loss_avg, vali_loss, mse])

            early_stopping(vali_loss, self.model, path)
            if early_stopping.early_stop:
                print("Early stopping")
                break
            
            adjust_learning_rate(model_optim, epoch + 1, self.args)

        # Plotting (Basic placeholder, user can run separate script or we add plot code here)
        import matplotlib.pyplot as plt
        df_log = pd.read_csv(log_path)
        plt.figure()
        plt.plot(df_log['epoch'], df_log['train_loss'], label='Train Loss')
        plt.plot(df_log['epoch'], df_log['vali_loss'], label='Val Loss')
        plt.legend()
        plt.savefig(os.path.join(path, "loss_plot.png"))
        print(f"Saved loss plot to {os.path.join(path, 'loss_plot.png')}")

        return self.model

def main():
    parser = argparse.ArgumentParser(description='Timer Sector Finetuning')
    
    # Data Paths
    parser.add_argument('--root_path', type=str, default='./model', help='root path of the data file')
    parser.add_argument('--data_path', type=str, default='sector_data.csv', help='data file')
    parser.add_argument('--checkpoints', type=str, default='./model/checkpoints/', help='location of model checkpoints')
    parser.add_argument('--pretrained_weight_path', type=str, default='', help='path to pretrained weights')
    parser.add_argument('--ckpt_path', type=str, default='', help='optional path to a specific .pth file')
    
    # Training Levers
    parser.add_argument('--seq_len', type=int, default=672, help='input sequence length (multiples of 96 recommended)')
    parser.add_argument('--label_len', type=int, default=336, help='start token length')
    parser.add_argument('--pred_len', type=int, default=96, help='prediction sequence length')
    parser.add_argument('--batch_size', type=int, default=16, help='batch size of training input data')
    parser.add_argument('--train_epochs', type=int, default=10, help='train epochs')
    parser.add_argument('--learning_rate', type=float, default=0.0001, help='optimizer learning rate')
    parser.add_argument('--train_layers_last', type=int, default=2, help='number of decoder layers to train (from end)')
    parser.add_argument('--accum_iter', type=int, default=1, help='gradient accumulation steps')
    parser.add_argument('--augment', action='store_true', help='apply Gaussian noise augmentation to training data')
    parser.add_argument('--early_stop_patience', type=int, default=3, help='patience for early stopping')
    
    # Optimization
    parser.add_argument('--loss', type=str, default='MSE', help='loss function')
    parser.add_argument('--use_weight_decay', action='store_true', help='use weight decay')
    parser.add_argument('--weight_decay', type=float, default=0.01, help='weight decay value')
    
    # Hardware / Speed
    parser.add_argument('--use_gpu', type=lambda x: (str(x).lower() == 'true'), default=True, help='use gpu')
    parser.add_argument('--gpu', type=int, default=0, help='gpu id')
    parser.add_argument('--num_workers', type=int, default=4, help='data loader num workers')

    args = parser.parse_args()
    
    # Hardcoded/Fixed Parameters for Timer-base-84m
    # These must match the pretrained model architecture
    fixed_params = {
        'task_name': 'forecast',
        'model': 'Timer',
        'data': 'custom',
        'features': 'M',
        'target': 'XLK',
        'freq': 't',
        'd_model': 512,
        'patch_len': 96,
        'e_layers': 6,
        'd_layers': 6,
        'n_heads': 8,
        'd_ff': 2048,
        'dropout': 0.1,
        'factor': 1,
        'activation': 'gelu',
        'output_attention': False,
        'embed': 'timeF',
        'lradj': 'type1',
        'use_multi_gpu': False,
        'local_rank': 0,
        'use_ims': False,
        'patience': args.early_stop_patience  # Sync patience
    }
    
    # Populate fixed params into args
    for k, v in fixed_params.items():
        setattr(args, k, v)
    
    # Handle GPU availability
    args.use_gpu = True if torch.cuda.is_available() and args.use_gpu else False
    
    print('Cleaned Args in experiment:')
    print(args)
    
    exp = Exp_Sector_Finetune(args)
    setting = 'Timer_Finetune_Sector_{}'.format(args.pred_len)
    
    print('>>>>>>> start training : {}>>>>>>>>>>>>>>>>>>>>>>>>>>'.format(setting))
    exp.finetune(setting)

if __name__ == "__main__":
    main()
