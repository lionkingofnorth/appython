#execute: predict.py 'flowers/test/1/image_06743.jpg' './checkpoint.pth'

from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision
from torchvision import datasets, transforms, models
from torch import nn, optim
from PIL import Image
import json
import seaborn as sb
import argparse


def parse():
    parser = argparse.ArgumentParser (description = "Set parser for prediction.")
    parser.add_argument ('image_path', help = 'Image path (required)', type = str)
    parser.add_argument ('model_path', help = 'Model checkpoint path (required).', type = str)
    parser.add_argument ('--top_k', help = 'Top K most likely classes.', default=5, type = int)
    parser.add_argument ('--category_names', help = 'JSON file name for mapping categories to flower names.', default='./cat_to_name.json', type = str)
    parser.add_argument ('--GPU', help = "Option to use 'GPU' (yes/no)", default='yes', type = str)
    

    args = parser.parse_args()

    return args


def device(args):
    if args.GPU == 'yes':
        args.device = 'cuda'
    elif args.GPU == 'no':
        args.device = 'cpu'
    return


def process_image(image_path):
    img = Image.open(image_path)    
    
    inference_transforms = transforms.Compose([transforms.Resize(255),
                                     transforms.CenterCrop(224),
                                     transforms.ToTensor(),
                                     transforms.Normalize([0.485, 0.456, 0.406],
                                                          [0.229, 0.224, 0.225])])
    
    img_tensor = inference_transforms(img)
    
    return img_tensor

def load_model(filepath):
    checkpoint = torch.load(filepath)
    model = checkpoint['model']
    #model.features = checkpoint['features']
    model.classifier = checkpoint['classifier']
    model.load_state_dict(checkpoint['state_dict'], strict=False)
    model.class_to_idx = checkpoint['class_to_idx']
    optimizer = checkpoint['optimizer']
    epochs = checkpoint['epochs']
                                
    for param in model.parameters():
        param.requires_grad = False
        
    return model, checkpoint['class_to_idx']

def predict_labels(model, args):
 
    ''' Predict the class (or classes) of an image using a trained deep learning model.
    '''
    image_path = args.image_path
    top_num = args.top_k
    # TODO: Implement the code to predict the class from an image file
    model.eval()
    
    with torch.no_grad():
    
        # Process image
        img = process_image(image_path)

        # Numpy -> Tensor
        image_tensor = img
        #print(image_tensor.device)
        image_tensor = image_tensor.to(args.device)
        #print(image_tensor.device)
        #print(image_tensor.shape)

        # Add batch of size 1 to image
        model_input = image_tensor.unsqueeze(0)
        #print(model_input.shape)
        
        model.to(args.device)
        logps = model(model_input)
        ps = torch.exp(logps)
        top_p, top_class = ps.topk(top_num, dim=1)

        # Convert indices to classes
        idx_to_class = {val: key for key, val in    
                                          model.class_to_idx.items()}
        
        #print(idx_to_class)
        top_labels=[]
        for c in top_class.cpu().numpy().tolist()[0]:
            top_labels.append(idx_to_class[c])
        #print('top_label: ', top_label)
        
        with open(args.category_names, 'r') as f:
            cat_to_name = json.load(f)
        
        top_flowers = [cat_to_name[str(lab)] for lab in top_labels]
        
    return top_p, top_labels, top_flowers



def main():
    args = parse()
    #print(args)
    device(args)
    img_tensor = process_image(args.image_path)
    #print(img_tensor)
    model,_ = load_model(args.model_path)
    print('loaded model succesfully')
    #print(model)
    top_p, top_labels, top_flowers = predict_labels(model, args)
    print('Top probabilities: ', top_p)
    print('Top labels: ', top_labels)
    print('Top flower names: ', top_flowers)
    
 
    
    
if __name__ == '__main__':
    main()