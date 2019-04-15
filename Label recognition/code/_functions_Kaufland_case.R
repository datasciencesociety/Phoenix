## function to return cropped to bounding box
fnCropToBB <- function(img, xmin, xmax, ymin, ymax) {
    image_crop(
        image = img, 
        geometry = paste0(xmax - xmin, "x", ymax - ymin, "+", xmin, "+", ymin)
    )
}

## Define helper function to extract the product code from the label, using original image and bounding box
fnExtractCodeFromLabel <- function(
    img, 
    xmin, xmax, ymin, ymax,
    eng,
    resize_to     = "3200!x2400!",
    code_position = "800x200+1100+1760"
) {
    #Takes an image, a bounding box, and returns the OCRed product code
    
    # resize_to     <- "1600!x1200!"
    # code_position <- "400x100+550+880"
    
    # resize_to     <- "3200!x2400!"
    # code_position <- "800x200+1100+1760"
    
    lbl_code_crop <- image_crop(
        image = image_contrast(
            sharpen = 0.75,
            image = image_scale(
                image = fnCropToBB(img = img, xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax), 
                geometry = resize_to # Rescale, do not preserve aspect
            )
        ), 
        geometry = code_position
    )
    
    ANS <- data.table(
        tesseract::ocr_data(
            image = lbl_code_crop, 
            engine = eng)
    )
    
    setnames(ANS, "bbox", "ocr_bbox")
    
    # Replace common OCR errors:
    ANS[, word := stringr::str_replace_all(string = word, pattern = "Q", replacement = "0")]
    ANS[, word := stringr::str_replace_all(string = word, pattern = "O", replacement = "0")]
    ANS[, word := stringr::str_replace_all(string = word, pattern = "o", replacement = "0")]
    
    return(ANS)
}

fnSingleImageSimilarityMatrix <- function(
    image_to_compare, 
    images_to_compare_to,
    ...
) {
    # Create a data.table with all pairwise combinations
    DT <- data.table(
        image_to_compare = image_to_compare,
        compared_to = images_to_compare_to 
    )
    
    DT[
        keyby = .(compared_to),
        j = dist := magick::image_compare_dist(
            image =           image_read(path = image_to_compare), 
            reference_image = image_read(path = compared_to)
        )]
    
    setkey(DT, image_to_compare, dist)
    return(DT)
}

fnPredictLabelFromImageCrop <- function(
    test_img,
    handpicked_images_path,
    engine = english
) {
    
    library(tesseract)
    library(magick)
    library(data.table)
    library(DescTools)
    
    #### Read in the image ------------------------------------------------------------------------------------------------
    img <- magick::image_read(path = test_img)
    img_dim <- dim(as.integer(img[1]))
    
    #### Do OCR prediction ------------------------------------------------------------------------------------------------
    # Do the OCR (on a sub-region of the label image -- approx. lower half/left side)
    OCR <- fnExtractCodeFromLabel(img = img, xmin = 1, xmax = img_dim[2], ymin = 1, ymax = img_dim[1], eng = engine)
    
    #### Compare image to the handpicked set ------------------------------------------------------------------------------
    # The handpicked labels -- "good quality" labels to compare the cropped image to
    handpicked_images_with_path <- dir(path = handpicked_images_path, full.names = TRUE)
    
    SIM <- NULL
    SIM <- fnSingleImageSimilarityMatrix(
        image_to_compare = test_img, 
        images_to_compare_to = handpicked_images_with_path, 
        metric = "MEPP", # MEPP = mean error per pixel (normalized mean error, normalized peak error)
        fuzz = 32 # 0-100, color distance allowed
    )
    
    #### Compare predictions ----------------------------------------------------------------------------------------------
    ## OCR best ----
    setkey(OCR, confidence)
    best_ocr <- last(OCR[nchar(word) %in% c(6, 7, 8, 9)])
    #cat("\nOCR prediction on original image: \n")
    # print(best_ocr)
    
    ## Handpicked best ----
    # SIM is sorted so that the 'best' match is in the last row.
    label_of_closest_image <- gsub(pattern = "^(.*)([0-9]{8})_(.*)$", replacement = "\\2", 
                                   x = last(SIM)$compared_to, 
                                   fixed = FALSE
    )
    
    #### Final decision ---------------------------------------------------------------------------------------------------
    if(nrow(best_ocr) > 0 && best_ocr$confidence >= 0.5) {
        # If we have an OCR prediction, use it if above 50% certain
        ret <- best_ocr$word
    } else {
        ret <- label_of_closest_image
    }
    
    return(ret)
}

