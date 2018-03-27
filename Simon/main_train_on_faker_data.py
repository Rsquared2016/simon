import Simon
import Encoder

def main(checkpoint, data_count, data_cols, should_train, nb_epoch, null_pct, try_reuse_data, batch_size, execution_config):
    maxlen = 20
    max_cells = 500
    p_threshold = 0.5

    Classifier = Simon()

    checkpoint_dir = "checkpoints/"
    if not os.path.isdir(checkpoint_dir):
        os.makedirs(checkpoint_dir)


    raw_data, header = DataGenerator.gen_test_data(
        (data_count, data_cols), try_reuse_data)
    print(raw_data)
    
    # transpose the data
    raw_data = np.char.lower(np.transpose(raw_data).astype('U'))
    
    # do other processing and encode the data
    if null_pct > 0:
        DataGenerator.add_nulls_uniform(raw_data, null_pct)
    config = {}
    if not should_train:
        if execution_config is None:
            raise TypeError
        config = load_config(execution_config, checkpoint_dir)
        encoder = config['encoder']
        if checkpoint is None:
            checkpoint = config['checkpoint']
    else:
        encoder = Encoder()
        encoder.process(raw_data, max_cells)
    
    # encode the data 
    X, y = encoder.encode_data(raw_data, header, maxlen)

    max_cells = encoder.cur_max_cells

    data = None
    if should_train:
        data = Classifier.setup_test_sets(X, y)
    else:
        data = type('data_type', (object,), {'X_test': X, 'y_test':y})

    print('Sample chars in X:{}'.format(X[2, 0:10]))
    print('y:{}'.format(y[2]))
    
    # need to know number of fixed categories to create model
    category_count = y.shape[1] 
    print('Number of fixed categories is :')
    print(category_count)
    
    model = Classifier.generate_model(maxlen, max_cells, category_count)
    
    load_weights(checkpoint, config, model, checkpoint_dir)
    
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['binary_accuracy'])
    if(should_train):
        start = time.time()
        train_model(batch_size, checkpoint_dir, model, nb_epoch, data)
        end = time.time()
        print("Time for training is %f sec"%(end-start))
        config = { 'encoder' :  encoder,
                   'checkpoint' : get_best_checkpoint(checkpoint_dir) }
        save_config(config, checkpoint_dir)
        
    print("DEBUG::The actual headers are:")
    print(header)
    evaluate_model(max_cells, model, data, encoder, p_threshold)

def resolve_file_path(filename, dir):
    if os.path.isfile(str(filename)):
        return str(filename)
    elif os.path.isfile(str(dir + str(filename))):
        return dir + str(filename)

def load_weights(checkpoint_name, config, model, checkpoint_dir):
    if config and not checkpoint_name:
        checkpoint_name = config['checkpoint']
    if checkpoint_name:
        checkpoint_path = resolve_file_path(checkpoint_name, checkpoint_dir)
        print("Checkpoint : %s" % str(checkpoint_path))
        model.load_weights(checkpoint_path)

def save_config(execution_config, checkpoint_dir):
    filename = ""
    if not execution_config["checkpoint"] is None:
        filename = execution_config["checkpoint"].rsplit( ".", 1 )[ 0 ] + ".pkl"
    else:
        filename = time.strftime("%Y%m%d-%H%M%S") + ".pkl"
    with open(checkpoint_dir + filename, 'wb') as output:
        pickle.dump(execution_config, output, pickle.HIGHEST_PROTOCOL)

def load_config(execution_config_path, dir):
    execution_config_path = resolve_file_path(execution_config_path, dir)
    return pickle.load( open( execution_config_path, "rb" ) )

def get_best_checkpoint(checkpoint_dir):
    max_mtime = 0
    max_file = ''
    for dirname,subdirs,files in os.walk(checkpoint_dir):
        for fname in files:
            full_path = os.path.join(dirname, fname)
            mtime = os.stat(full_path).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                max_dir = dirname
                max_file = fname
    return max_file

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='attempts to discern data types looking at columns holistically.')

    parser.add_argument('--cp', dest='checkpoint',
                        help='checkpoint to load')

    parser.add_argument('--config', dest='execution_config',
                        help='execution configuration to load. contains max_cells, and encoder config.')

    parser.add_argument('--train', dest='should_train', action="store_true",
                        default="True", help='run training')
    parser.add_argument('--no_train', dest='should_train', action="store_false",
                        default="True", help='do not run training')
    parser.set_defaults(should_train=True)

    parser.add_argument('--data_count', dest='data_count', action="store", type=int,
                        default=100, help='number of data rows to create')
    parser.add_argument('--data_cols', dest='data_cols', action="store", type=int,
                        default=10, help='number of data cols to create')
    parser.add_argument('--nullpct', dest='null_pct', action="store", type=float,
                        default=0, help='percent of Nulls to put in each column')

    parser.add_argument('--nb_epoch', dest='nb_epoch', action="store", type=int,
                        default=5, help='number of epochs')
    parser.add_argument('--try_reuse_data', dest='try_reuse_data', action="store_true",
                        default="True", help='loads existing data if the dimensions have been stored')
    parser.add_argument('--force_new_data', dest='try_reuse_data', action="store_false",
                        default="True", help='forces the creation of new data, even if the dimensions have been stored')
    parser.add_argument('--batch_size', dest='batch_size', action="store", type=int,
                        default=64, help='batch size for training')

    args = parser.parse_args()

    main(args.checkpoint, args.data_count, args.data_cols, args.should_train,
         args.nb_epoch, args.null_pct, args.try_reuse_data, args.batch_size, args.execution_config)