import os
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler

class SectorDataset(Dataset):
    def __init__(self, root_path, flag='train', size=None,
                 features='M', data_path='sector_data.csv',
                 target='XLK', scale=True, timeenc=0, freq='t'):
        # size [seq_len, label_len, pred_len]
        if size is None:
            self.seq_len = 96
            self.label_len = 48
            self.pred_len = 96
        else:
            self.seq_len = size[0]
            self.label_len = size[1]
            self.pred_len = size[2]

        assert flag in ['train', 'test', 'val']
        type_map = {'train': 0, 'val': 1, 'test': 2}
        self.set_type = type_map[flag]

        self.features = features
        self.target = target
        self.scale = scale
        self.timeenc = timeenc
        self.freq = freq

        self.root_path = root_path
        self.data_path = data_path
        self.__read_data__()

    def __read_data__(self):
        self.scaler = StandardScaler()
        df_raw = pd.read_csv(os.path.join(self.root_path, self.data_path))
        
        # Rename timestamp to date if needed
        if 'timestamp' in df_raw.columns:
            df_raw.rename(columns={'timestamp': 'date'}, inplace=True)
            
        # Ensure date is the first column
        cols = list(df_raw.columns)
        if 'date' in cols:
            cols.remove('date')
            df_raw = df_raw[['date'] + cols]
        
        # Split train/val/test
        # 70% train, 20% val, 10% test
        num_train = int(len(df_raw) * 0.7)
        num_test = int(len(df_raw) * 0.1) # Reduced test size to give more to val
        num_vali = len(df_raw) - num_train - num_test
        
        border1s = [0, num_train - self.seq_len, len(df_raw) - num_test - self.seq_len]
        border2s = [num_train, num_train + num_vali, len(df_raw)]
        border1 = border1s[self.set_type]
        border2 = border2s[self.set_type]

        if self.features == 'M' or self.features == 'MS':
            cols_data = df_raw.columns[1:]
            df_data = df_raw[cols_data]
        elif self.features == 'S':
            df_data = df_raw[[self.target]]

        if self.scale:
            train_data = df_data[border1s[0]:border2s[0]]
            self.scaler.fit(train_data.values)
            data = self.scaler.transform(df_data.values)
        else:
            data = df_data.values

        # Time encoding
        df_stamp = df_raw[['date']][border1:border2]
        df_stamp['date'] = pd.to_datetime(df_stamp.date)
        
        # Placeholder for time features if needed, or simple encoding
        # Timer typically uses time features.
        # We can reuse utils.timefeatures if we import them, or just use zeros if embed='fixed' or similar.
        # But let's try to do it properly.
        # For now, just return zeros for mark if we don't have the utils imported.
        # We will handle import in finetune script and pass the class. 
        # But this class needs to be standalone?
        # I'll rely on the caller to inject time_features or just use a simple one here.
        
        data_stamp = np.zeros((len(df_stamp), 4)) # Placeholder [Month, Day, Weekday, Hour]?

        self.data_x = data[border1:border2]
        self.data_y = data[border1:border2]
        self.data_stamp = data_stamp

    def __getitem__(self, index):
        s_begin = index
        s_end = s_begin + self.seq_len
        r_begin = s_end - self.label_len
        r_end = r_begin + self.label_len + self.pred_len

        seq_x = self.data_x[s_begin:s_end]
        seq_y = self.data_y[r_begin:r_end]
        seq_x_mark = self.data_stamp[s_begin:s_end]
        seq_y_mark = self.data_stamp[r_begin:r_end]

        return seq_x, seq_y, seq_x_mark, seq_y_mark

    def __len__(self):
        return len(self.data_x) - self.seq_len - self.pred_len + 1

    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data)
