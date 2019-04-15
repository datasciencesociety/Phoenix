#### Takes a label image, and returns a predicted product code

library(tesseract)
library(magick)
library(data.table)
library(DescTools)

source(file = "code/_functions_Kaufland_case.R")

# Define the language for tesseract 
# bulgarian <- tesseract(language = "bul") # Discarded, does not work well with digits
english  <- tesseract(language = "eng")


### Test a single image:

fnPredictLabelFromImageCrop(
    test_img = "data/test_images/0623.jpg", 
    handpicked_images_path = "data/labels_best_handpicked/"
)

