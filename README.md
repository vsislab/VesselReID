# 1. VesselReID Dataset Introduction
To facilitate the research of vessel re-identification, we build the VesselReID dataset that consists of 30,587 images of 1,248 vessels. Each vessel in VesselReID has a number of images captured at various times, places, and viewpoints as well as under different weather conditions.

Following the normal settings in most popular re-ID datasets, we split the entire dataset into training and testing sets. We randomly select 624 vessel identities (half of the vessel identities) for training, while images of the other 624 vessels are used for testing. Therefore, there is no validation set in the original VesselReID dataset, and the re-ID models are supposed to be evaluated on the test set during the training. Moreover, we additionally divide the VesselReID dataset into training, validating and testing sets as an extra split, where there are 550 vessel identities in both training and testing sets while the remaining 148 vessel identities are utilised for validation.

See more details in our paper.

# 2. Dataset Availability
To encourage the research in terms of vessel re-identification, we are pleased to provide the VesselReID dataset according to your request. 
If you want to use our dataset for research, you can contact us via sending an email to *info@vsislab.com*. We will make the dataset available to you by providing the file needed for a download.
When contacting us, please state your full name and affiliation. 
We ask for your information only to make sure the dataset is used for non-commercial purposes. 

# 3. Download

```python
conda create -n demo python=3.6
conda activate demo
pip install -r requirements.txt
python demo.py --pth '$path$/VesselReID.json' --save_pth '$path$/datasets/VesselReID'    # pth is the address of the annotations file and save_pth is the address where the data set is downloaded and saved
```
The needed file titled 'VesselReID.json' can only be obtained by email.

# 4. Citation
If you find VesselReID Dataset useful in your work, please cite our paper:

```
```
