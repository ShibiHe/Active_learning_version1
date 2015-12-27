import subprocess

class LibFM(object):
    
    def __init__(self, data_dir="./Generate/"):
        self.data_dir = data_dir

    def run(self, task, train_file, test_file, method="mcmc", iter_num=100, out="prediction"):
        subprocess.call(data_dir + "libFM -task " + task \
            + " -train " + train_file + " -test " + test_file \
            + " -method " + method + " -iter " + iter_num \
            + " -out " + out, shell=True)
        
