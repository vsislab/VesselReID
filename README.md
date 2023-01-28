# 1. VesselReID Dataset Introduction
(Please click [**here**](http://www.vsislab.com/) to the new webpage.)



# 2. Dataset Availability
To encourage related research, we will provide the dataset according to your request. 
We will make the dataset available to you in two ways, either by sharing the full data or by providing a download.
Please email your full name and affiliation and sign a license agreement to the contact person (*info at vsislab dot com*). 
We ask for your information only to make sure the dataset is used for non-commercial purposes. 
We will not give it to any third party or publish it publicly anywhere.

# 3. Download
We recommend Anaconda as Python package management system. Annotations file name as 'VesselReID.json', please obtain the file by email .

```python
conda create -n demo python=3.6
conda activate demo
pip install -r requirements.txt
python demo.py --pth '$path$/VesselReID.json' --save_pth '$path$/datasets/VesselReID'    # pth is the address of the annotations file and save_pth is the address where the data set is downloaded and saved
```

# 4. Citation
If you find VesselReID Dataset useful in your work, please consider citing the following BibTeX entry:

```
```