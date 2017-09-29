# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 15:45:17 2017

@author: Anjan Dutta
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 12:24:27 2017

@author: adutta
"""

import numpy as np
np.random.seed(0)  # for reproducibility
from keras.layers import Dense, Dropout, Input, Lambda, Flatten, Convolution2D, MaxPooling2D, ZeroPadding2D
from scipy import linalg
from keras.preprocessing import image
from keras import backend as K
import getpass as gp
import warnings
from keras.models import Sequential, Model
from keras.optimizers import SGD, RMSprop
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
import random
random.seed(0)

class SignatureData(object):    
    
    def __init__(self, dataset, tot_writers, num_train_writers, num_valid_writers,
                 num_test_writers, batch_sz, img_height, img_width,
                 featurewise_center=False,
                 featurewise_std_normalization=False,
                 zca_whitening=False):
        
        # check whether the total number of writers are less than num_train_writers + num_valid_writers + num_test_writers
        assert tot_writers >= num_train_writers + num_valid_writers + num_test_writers, 'Total writers is less than train and test writers'
        
        self.featurewise_center = featurewise_center
        self.featurewise_std_normalization = featurewise_std_normalization
        self.zca_whitening = zca_whitening
        
        usr = gp.getuser()        
        
        if(dataset=='GPDS960' or dataset=='GPDS300' or dataset == 'Hindi' or dataset == 'Bengali'):
            size = 996            
        elif(dataset=='CEDAR1'):
            size = 852

        nsamples = 276 #24C2
                    
        self.image_dir = '/home/' + usr + '/Workspace/Datasets/' + dataset + '/'
        data_file = self.image_dir + dataset + '_pairs.txt'
        
        idx_writers = list(range(tot_writers))
        
        idx_train_writers = sorted(np.random.choice(idx_writers, num_train_writers, replace=False))
        idx_valid_writers = sorted(np.random.choice([x for x in idx_writers if x not in idx_train_writers], num_valid_writers, replace=False))
        idx_test_writers = sorted(np.random.choice([x for x in idx_writers if x not in idx_train_writers and x not in idx_valid_writers], num_test_writers, replace=False))
        
        idx_train_lines = []
        for iw in idx_train_writers:
            idx_train_lines += list(range(iw * size, (iw + 1) * size))
            
        idx_valid_lines = []
        for iw in idx_valid_writers:
            idx_valid_lines += list(range(iw * size, (iw + 1) * size))
        
        idx_test_lines = []
        for iw in idx_test_writers:
            idx_test_lines += list(range(iw * size, (iw + 1) * size))
            
        f = open( data_file, 'r' )
        lines = f.readlines()
        f.close()        

        train_lines = [lines[i] for i in idx_train_lines]
        valid_lines = [lines[i] for i in idx_valid_lines]
        test_lines = [lines[i] for i in idx_test_lines]

        del lines
        
        # for train writers    
        idx_lines = []
    
        lp = []
        lin = []
    
        for iline, line in enumerate(train_lines):            
            
            file1, file2, label = line.split(' ')
            
            label = int(label)
            
            lp += [label]        
            lin += [iline]
            
            if(len(lp) != 0 and len(lp) % size == 0):                
                            
                idx1 = [i for i, x in enumerate(lp) if x == 1]
                idx2 = [i for i, x in enumerate(lp) if x == 0]
                
                idx1 = np.random.choice(idx1, nsamples)
                idx2 = np.random.choice(idx2, nsamples)
                
                idx = [None]*(len(idx1)+len(idx2))
                
                idx[::2] = idx1
                idx[1::2] = idx2
                
                del idx1
                del idx2
                
                idx_lines += [lin[i] for i in idx]
                
                lp = []
                lin = []            
            
        self.train_lines = [train_lines[i] for i in idx_lines]

        just_1 = self.train_lines[0:][::2]
        just_0 = self.train_lines[1:][::2]
        random.shuffle(just_1)
        random.shuffle(just_0)
        self.train_lines= [item for sublist in zip(just_1,just_0) for item in sublist]
        
        # for valid writers    
        idx_lines = []
    
        lp = []
        lin = []
    
        for iline, line in enumerate(valid_lines):            
            
            file1, file2, label = line.split(' ')
            
            label = int(label)
            
            lp += [label]        
            lin += [iline]
            
            if(len(lp) != 0 and len(lp) % size == 0):                
                            
                idx1 = [i for i, x in enumerate(lp) if x == 1]
                idx2 = [i for i, x in enumerate(lp) if x == 0]
                
                idx1 = np.random.choice(idx1, nsamples)
                idx2 = np.random.choice(idx2, nsamples)
                
                idx = [None]*(len(idx1)+len(idx2))
                
                idx[::2] = idx1
                idx[1::2] = idx2
                
                del idx1
                del idx2
                
                idx_lines += [lin[i] for i in idx]
                
                lp = []
                lin = []            
            
        self.valid_lines = [valid_lines[i] for i in idx_lines]

        just_1 = self.valid_lines[0:][::2]
        just_0 = self.valid_lines[1:][::2]
        random.shuffle(just_1)
        random.shuffle(just_0)
        self.valid_lines= [item for sublist in zip(just_1,just_0) for item in sublist]
        
        # for test writers
        idx_lines = []
    
        lp = []
        lin = []
    
        for iline, line in enumerate(test_lines):            
            
            file1, file2, label = line.split(' ')
            
            label = int(label)
            
            lp += [label]        
            lin += [iline]
            
            if(len(lp) != 0 and len(lp) % size == 0):                
                            
                idx1 = [i for i, x in enumerate(lp) if x == 1]
                idx2 = [i for i, x in enumerate(lp) if x == 0]
                
                idx1 = np.random.choice(idx1, nsamples)
                idx2 = np.random.choice(idx2, nsamples)
                
                idx = [None]*(len(idx1)+len(idx2))
                
                idx[::2] = idx1
                idx[1::2] = idx2
                
                del idx1
                del idx2
                
                idx_lines += [lin[i] for i in idx]
                
                lp = []
                lin = []       

        self.test_lines = [test_lines[i] for i in idx_lines]

        just_1 = self.test_lines[0:][::2]
        just_0 = self.test_lines[1:][::2]
        random.shuffle(just_1)
        random.shuffle(just_0)
        self.test_lines= [item for sublist in zip(just_1,just_0) for item in sublist]
        
        # Set other parameters
        self.height=img_height
        self.width=img_width
        self.input_shape=(self.height, self.width, 1)
        self.cur_train_index = 0
        self.cur_valid_index = 0
        self.cur_test_index = 0
        self.batch_sz = batch_sz
        self.samples_per_train = 2*nsamples*num_train_writers
        self.samples_per_valid = 2*nsamples*num_valid_writers
        self.samples_per_test = 2*nsamples*num_test_writers
        # Incase dim_ordering = 'tf'
        self.channel_axis = 3
        self.row_axis = 1
        self.col_axis = 2
        
        self.train_labels = np.array([float(line.split(' ')[2].strip('\n')) for line in self.train_lines])
        self.valid_labels = np.array([float(line.split(' ')[2].strip('\n')) for line in self.valid_lines])
        self.test_labels = np.array([float(line.split(' ')[2].strip('\n')) for line in self.test_lines])
        
    def next_train(self):
        while True:            
            image_pairs = []
            label_pairs = []
            
            if self.cur_train_index + self.batch_sz >= self.samples_per_train:
                self.cur_train_index=0
            
            cur_train_index = self.cur_train_index + self.batch_sz
             
            if(cur_train_index > len(self.train_lines)):
                cur_train_index = len(self.train_lines)
            
            idx = list(range(self.cur_train_index, cur_train_index))            
            
            lines = [self.train_lines[i] for i in idx]                
                
            for line in lines:
                file1, file2, label = line.split(' ')
                
                img1 = image.load_img(self.image_dir + file1, grayscale = True,
                target_size=(self.height, self.width))
                                
                img1 = image.img_to_array(img1, dim_ordering='tf')
                
                img1 = self.standardize(img1)
                                
                img2 = image.load_img(self.image_dir + file2, grayscale = True,
                target_size=(self.height, self.width))
                
                img2 = image.img_to_array(img2, dim_ordering='tf')
                
                img2 = self.standardize(img2)
                
                image_pairs += [[img1, img2]]
                label_pairs += [int(label)]
                
            self.cur_train_index = cur_train_index
            
            images = [np.array(image_pairs)[:,0], np.array(image_pairs)[:,1]]
            labels = np.array(label_pairs)
            return (images, labels)
                
    def next_valid(self):
        while True:            
            image_pairs = []
            label_pairs = []
            
            if self.cur_valid_index_index + self.batch_sz >= self.samples_per_valid:
                self.cur_valid_index=0
            
            cur_valid_index = self.cur_valid_index + self.batch_sz
            
            if(cur_valid_index > len(self.valid_lines)):
                cur_valid_index = len(self.valid_lines)
            
            idx = list(range(self.cur_valid_index, cur_valid_index))
            
            lines = [self.valid_lines[i] for i in idx]
                
            for line in lines:
                file1, file2, label = line.split(' ')
                
                img1 = image.load_img(self.image_dir + file1, grayscale = True,
                target_size=(self.height, self.width))
                
                img1 = image.img_to_array(img1, dim_ordering='tf')
                
                img1 = self.standardize(img1)
                                
                img2 = image.load_img(self.image_dir + file2, grayscale = True,
                target_size=(self.height, self.width))
                
                img2 = image.img_to_array(img2, dim_ordering='tf')
                
                img2 = self.standardize(img2)
                
                image_pairs += [[img1, img2]]
                label_pairs += [int(label)]

            self.cur_valid_index = cur_valid_index
            images = [np.array(image_pairs)[:,0], np.array(image_pairs)[:,1]]
            labels = np.array(label_pairs)

            return (images, labels)
                
    def next_test(self):
        while True:            
            image_pairs = []
            label_pairs = []
            
            if self.cur_test_index + self.batch_sz >= self.samples_per_test:
                self.cur_test_index=0
            
            cur_test_index = self.cur_test_index + self.batch_sz
            
            if(cur_test_index > len(self.test_lines)):
                cur_test_index = len(self.test_lines)            
            
            idx = list(range(self.cur_test_index, cur_test_index))
            
            lines = [self.test_lines[i] for i in idx]
                
            for line in lines:
                file1, file2, label = line.split(' ')
                
                img1 = image.load_img(self.image_dir + file1, grayscale = True,
                target_size=(self.height, self.width))
                
                img1 = image.img_to_array(img1, dim_ordering='tf')
                
                img1 = self.standardize(img1)
                
                img2 = image.load_img(self.image_dir + file2, grayscale = True,
                target_size=(self.height, self.width))
                
                img2 = image.img_to_array(img2, dim_ordering='tf')
                
                img2 = self.standardize(img2)
                
                image_pairs += [[img1, img2]]
                label_pairs += [int(label)]

            self.cur_test_index = cur_test_index
            images = [np.array(image_pairs)[:,0], np.array(image_pairs)[:,1]]

            return (images)
            
    def fit(self, x, augment=False, rounds=1, seed=None):
        
        x = np.asarray(x, dtype=K.floatx())
        if x.ndim != 4:
            raise ValueError('Input to `.fit()` should have rank 4. '
                             'Got array with shape: ' + str(x.shape))
        if x.shape[self.channel_axis] not in {1, 3, 4}:
            raise ValueError(
                'Expected input to be images (as Numpy array) '
                'following the dimension ordering convention "' + self.dim_ordering + '" '
                '(channels on axis ' + str(self.channel_axis) + '), i.e. expected '
                'either 1, 3 or 4 channels on axis ' + str(self.channel_axis) + '. '
                'However, it was passed an array with shape ' + str(x.shape) +
                ' (' + str(x.shape[self.channel_axis]) + ' channels).')

        if seed is not None:
            np.random.seed(seed)

        x = np.copy(x)
        if augment:
            ax = np.zeros(tuple([rounds * x.shape[0]] + list(x.shape)[1:]), dtype=K.floatx())
            for r in range(rounds):
                for i in range(x.shape[0]):
                    ax[i + r * x.shape[0]] = self.random_transform(x[i])
            x = ax

        if self.featurewise_center:
            self.mean = np.mean(x, axis=(0, self.row_axis, self.col_axis))
            broadcast_shape = [1, 1, 1]
            broadcast_shape[self.channel_axis - 1] = x.shape[self.channel_axis]
            self.mean = np.reshape(self.mean, broadcast_shape)
            x -= self.mean

        if self.featurewise_std_normalization:
            self.std = np.std(x, axis=(0, self.row_axis, self.col_axis))
            broadcast_shape = [1, 1, 1]
            broadcast_shape[self.channel_axis - 1] = x.shape[self.channel_axis]
            self.std = np.reshape(self.std, broadcast_shape)
            x /= (self.std + K.epsilon())

        if self.zca_whitening:
            flat_x = np.reshape(x, (x.shape[0], x.shape[1] * x.shape[2] * x.shape[3]))
            sigma = np.dot(flat_x.T, flat_x) / flat_x.shape[0]
            u, s, _ = linalg.svd(sigma)
            self.principal_components = np.dot(np.dot(u, np.diag(1. / np.sqrt(s + 10e-7))), u.T)
            
    def standardize(self, x):
        
        if self.featurewise_center:
            if self.mean is not None:
                x -= self.mean
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`featurewise_center`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        if self.featurewise_std_normalization:
            if self.std is not None:
                x /= (self.std + 1e-7)
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`featurewise_std_normalization`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        if self.zca_whitening:
            if self.principal_components is not None:
                flatx = np.reshape(x, (x.size))
                whitex = np.dot(flatx, self.principal_components)
                x = np.reshape(whitex, (x.shape[0], x.shape[1], x.shape[2]))
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`zca_whitening`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        return x
        
def euclidean_distance(vects):
    x, y = vects
    return K.sqrt(K.sum(K.square(x - y), axis=1, keepdims=True))


def eucl_dist_output_shape(shapes):
    shape1, shape2 = shapes
    return (shape1[0], 1)


def contrastive_loss(y_true, y_pred):
    '''Contrastive loss from Hadsell-et-al.'06
    http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
    '''
    margin = 1
    return K.mean(y_true * K.square(y_pred) + (1 - y_true) * K.square(K.maximum(margin - y_pred, 0)))

def create_base_network1(input_shape):
    '''Base network to be shared (eq. to feature extraction).
    '''
    seq = Sequential()
    seq.add(Flatten(name='flatten', input_shape=input_shape))
    seq.add(Dense(128, activation='relu'))
    seq.add(Dropout(0.1))
    seq.add(Dense(128, activation='relu'))
    seq.add(Dropout(0.1))
    seq.add(Dense(128, activation='relu'))
    return seq
    
def create_base_network2(input_shape):
    '''Base network to be shared (eq. to feature extraction).
    '''
    seq = Sequential()
    seq.add(Convolution2D(20, 11, 11, activation='relu', border_mode='same', input_shape=input_shape, name='block1_conv1', subsample=(1, 1), init='glorot_uniform'))
    seq.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='block1_pool', dim_ordering='tf'))
    
    seq.add(Flatten(name='flatten'))
    seq.add(Dense(128,  activation='relu', name='fc1'))
    seq.add(Dropout(0.5))
    seq.add(Dense(128, activation='relu', name='fc2'))
    seq.add(Dropout(0.5))
    seq.add(Dense(128, activation='relu', name='fc3'))
    
    return seq
    
def create_base_network3(input_shape):    
    '''Base network to be shared (eq. to feature extraction).
    '''
    seq = Sequential()
    seq.add(Convolution2D(20, 11, 11,  activation='relu', border_mode='same', input_shape=input_shape, name='block1_conv1', subsample=(1, 1), init='glorot_uniform'))
    seq.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='block1_pool', dim_ordering='tf'))
    
    seq.add(Convolution2D(50, 5, 5, activation='relu', border_mode='same', name='block2_conv1', subsample=(1, 1), init='glorot_uniform'))
    seq.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='block2_pool', dim_ordering='tf'))
    
    seq.add(Flatten(name='flatten'))
    seq.add(Dense(128,  W_regularizer=l2(0.0005), activation='relu', name='fc1'))
    seq.add(Dropout(0.1))
    seq.add(Dense(128, W_regularizer=l2(0.0005), activation='relu', name='fc2'))
    seq.add(Dropout(0.1))
    seq.add(Dense(128, W_regularizer=l2(0.0005), activation='relu', name='fc3'))
    
    return seq
    
def create_base_network_ijcnn(input_shape):
    
    model = Sequential()
    model.add(Convolution2D(96, 11, 11, activation='relu', name='conv1_1', subsample=(4, 4),input_shape= input_shape, 
                        init='glorot_uniform', dim_ordering='tf'))
    model.add(BatchNormalization(epsilon=1e-06, mode=0, axis=1, momentum=0.9))
    model.add(MaxPooling2D((3,3), strides=(2, 2)))
    
    model.add(ZeroPadding2D((2, 2), dim_ordering='tf'))
    model.add(Convolution2D(256, 5, 5, activation='relu', name='conv2_1', subsample=(1, 1), init='glorot_uniform',  dim_ordering='tf'))
    model.add(BatchNormalization(epsilon=1e-06, mode=0, axis=1, momentum=0.9))
    model.add(MaxPooling2D((3,3), strides=(2, 2)))
    
    model.add(ZeroPadding2D((1, 1), dim_ordering='tf'))
    model.add(Convolution2D(384, 3, 3, activation='relu', name='conv3_1', subsample=(1, 1), init='glorot_uniform',  dim_ordering='tf'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='tf'))
    model.add(Convolution2D(256, 3, 3, activation='relu', name='conv3_2', subsample=(1, 1), init='glorot_uniform', dim_ordering='tf'))
    
    model.add(MaxPooling2D((3,3), strides=(2, 2)))
    model.add(Flatten(input_shape=model.output_shape[1:]))
    model.add(Dense(4096, W_regularizer=l2(0.0005), activation='relu', init='glorot_uniform'))
    model.add(Dropout(0.5))
    
    model.add(Dense(1000, W_regularizer=l2(0.0005), activation='softmax', init='glorot_uniform'))
    return model

def compute_accuracy(predictions, labels):
    '''Compute classification accuracy with a fixed threshold on distances.
    '''
    return labels[predictions.ravel() < 0.5].mean()
    
def read_signature_data(dataset, ntuples, height = 30, width = 100):
    
    usr = gp.getuser()

    image_dir = '/home/' + usr + '/Workspace/Datasets/' + dataset + '/'
    data_file = image_dir + dataset + '_pairs.txt'
    
    f = open( data_file, 'r' )
    lines = f.readlines()
    f.close()
    
#    print ('lines', lines)
#    print('ntuples', ntuples)
    idx = np.random.choice(list(range(len(lines))), ntuples)
    
    lines = [lines[i] for i in idx]
    
    images = []
    
    for line in lines:
        file1, file2, label = line.split(' ')
                                       
        img1 = image.load_img(image_dir + file1, grayscale = True, 
                target_size=(height, width))
                
        img1 = image.img_to_array(img1, dim_ordering='tf')
                
        images.append(img1)
        
        img2 = image.load_img(image_dir + file1, grayscale = True, 
                target_size=(height, width))
            
        img2 = image.img_to_array(img2, dim_ordering='tf')
                
        images.append(img2)
        
    return np.array(images)
        
def main():
    
    dataset = 'GPDS960'
    
    if dataset == 'Bengali':
    
        tot_writers = 100
        num_train_writers = 5
        num_valid_writers = 5
        
    elif dataset == 'Hindi':
        
        tot_writers = 160
        num_train_writers = 100
        num_valid_writers = 10
        
    elif dataset == 'GPDS300':
    
        tot_writers = 300
        num_train_writers = 200
        num_valid_writers = 10
        
    elif dataset == 'GPDS960':
    
        tot_writers = 4000
        num_train_writers = 2
        num_valid_writers = 1
        
    elif dataset == 'CEDAR1':
    
        tot_writers = 55
        num_train_writers = 50
        num_valid_writers = 10
    
#    num_test_writers = tot_writers - num_train_writers
    num_test_writers = 5
        
    batch_sz = 1
    img_height = 155
    img_width = 220
    featurewise_center = False
    featurewise_std_normalization = True
    zca_whitening = False
    nb_epoch = 20
    
    input_shape=(img_height, img_width, 1)
    
    datagen = SignatureData(dataset, tot_writers, num_train_writers, 
        num_valid_writers, num_test_writers, batch_sz, img_height, img_width,
        featurewise_center, featurewise_std_normalization, zca_whitening)
    
    #data fit for std
    X_sample = read_signature_data(dataset, int(round(0.5*tot_writers)), height=img_height, width=img_width)
    datagen.fit(X_sample)
    del X_sample
    
    # network definition
    base_network = create_base_network3(input_shape)
    
    input_a = Input(shape=(input_shape))
    input_b = Input(shape=(input_shape))
    
    # because we re-use the same instance `base_network`,
    # the weights of the network
    # will be shared across the two branches
    processed_a = base_network(input_a)
    processed_b = base_network(input_b)
    
    distance = Lambda(euclidean_distance, output_shape=eucl_dist_output_shape)([processed_a, processed_b])
    
    model = Model(input=[input_a, input_b], output=distance)
    
    # Train model
    rms = RMSprop(lr=0.000001)
    model.compile(loss=contrastive_loss, optimizer=rms)
    
    steps = int(round(datagen.samples_per_train/batch_sz))
#    print steps    
    for iepoch in range(nb_epoch):
        accs = []
        losses = []
        for isteps in range(steps):
            x, y = datagen.next_train()
            
            l, a = model.train_on_batch(x, y)
            accs.append(a)
            losses.append(l)
            print (np.mean(losses),np.mean(accs))
            model.sample_weights('test.h5', overwrite=True)
#        
#        
#        
#        
#        
#        
#        
#    model.fit_generator(generator=datagen.next_train(), samples_per_epoch=datagen.samples_per_train, nb_epoch=nb_epoch, validation_data=datagen.next_valid(), nb_val_samples=int(datagen.samples_per_valid))
#        
#    tr_pred = model.predict_generator(generator=datagen.next_train(), val_samples=int(datagen.samples_per_train))
#    te_pred = model.predict_generator(generator=datagen.next_test(), val_samples=int(datagen.samples_per_test))
#    
#    tr_acc = compute_accuracy(tr_pred, datagen.train_labels)
#    te_acc = compute_accuracy(te_pred, datagen.test_labels)
#    
#    print('* Accuracy on training set: %0.2f%%' % (100 * tr_acc))
#    print('* Accuracy on test set: %0.2f%%' % (100 * te_acc))
    
if __name__ == "__main__":
    main()