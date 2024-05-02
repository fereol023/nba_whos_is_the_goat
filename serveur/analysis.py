from utils.mongo_controller import *
from sklearn.manifold import TSNE
from sklearn.decomposition  import PCA
import os

class Analyzer:

    def __init__(self) -> None:
        self.careers_data = CareersController().find_all_numeric_and_names()
        self.root = 'analysis_res/'
        if not os.path.exists(self.root):
            os.mkdir(self.root)

    def tsne_reduction(self, n_comp=2):
        df = self.careers_data.dropna()
        X = df[[c for c in df.columns if c != 'full_name']].dropna()
        y = df['full_name'].values
        Xres = TSNE(n_components=n_comp, perplexity=5, random_state=0).fit_transform(X)
        #print(Xres)
        #print(y)
        #self.save_as_res(Xres)
        return {'names': list(y), 'weights': Xres.tolist()}
    
    def save_as_res(self, n, obj):
        #obj.to_pickle(f'{self.root}/{n}.pkl')
        pass

    def pca_reduction(self, n_comp=2):
        df = self.careers_data.dropna()
        X = df[[c for c in df.columns if c != 'full_name']].dropna()
        y = df['full_name'].values
        Xres = Xres = PCA(n_components=n_comp).fit_transform(X)
        return {'names': list(y), 'weights': Xres.tolist()}