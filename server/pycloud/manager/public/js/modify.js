
/////////////////////////////////////////////////////////////////////////////////////
// Checks that the minimum inputs have been submitted.
/////////////////////////////////////////////////////////////////////////////////////
function validateSubmission()
{
    // Get all the edited fields of the svm.
    var svm_info = {};
    svm_info.serviceId = $('#serviceID').val();
    svm_info.port = $('#servicePort').val();
    svm_info.folder = $('#vmStoredFolder').val();
    
    // Validate that we have all the necessary info.
    if(!validateMandatoryField(svm_info.serviceId, "Service Id")) return false;
    if(!validateMandatoryField(svm_info.port, "Service Port")) return false;
    if(!validateMandatoryField(svm_info.folder, "VM Image")) return false;
        
    // If everything is ok, submit the form.
    var serviceForm = $('#service-form');    
    serviceForm.submit();
    return true;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to update buttons and fields after a VM image is selected.
/////////////////////////////////////////////////////////////////////////////////////
function showImageInfoAndButtons(vm_image)
{
    // Update Stored SVM fields with new SVM info.
    $('#vmStoredFolder').val(getFileDirectory(vm_image.disk_image));
    $('#vmDiskImageFile').val(vm_image.disk_image);
    $('#vmDiskImageFileValue').val(vm_image.disk_image);
    $('#vmStateImageFile').val(vm_image.state_image);
    $('#vmStateImageFileValue').val(vm_image.state_image);

    // Update the buttons to reflect that we can now modify the SVM.
    $('#modify-svm-button').show();
    $('#choose-image-button').show();

    $('#new-svm-button').hide();
    $('#save-svm-button').hide();
    $('#discard-svm-button').hide();
    $('#vnc-button').hide();
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to update buttons and fields when an SVM is created to create/modify an image.
/////////////////////////////////////////////////////////////////////////////////////
function showServiceVMButtons(svm)
{
    // Update the buttons to reflect that we can now save or discard the SVM.
    $('#svmInstanceId').val(svm._id);
    $('#new-svm-button').hide();
    $('#modify-svm-button').hide();
    $('#choose-image-button').hide();

    $('#save-svm-button').show();
    $('#discard-svm-button').show();
    $('#vnc-button').show();
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to set an existing VM Image to a service.
/////////////////////////////////////////////////////////////////////////////////////
function chooseImage()
{
    // Get basic information about the form with the new svm.
    var imageForm = $('#choose-image-form');
    var serviceForm = $('#service-form');
    var actionURL = imageForm.attr('action');

    // Get all the edited fields of the image.
    var image_info = {};
    image_info.folder = imageForm.find('#vmImageFolder').val();
    image_info.port = serviceForm.find('#servicePort').val();
    image_info.serviceId = serviceForm.find('#serviceID').val();
    var jsonData = JSON.stringify(image_info);

    // Validate that we have all the necessary info.
    var modalDiv = $('#modal-choose-image');
    if(!validateMandatoryField(image_info.serviceId, "Service Id", modalDiv)) return false;
    if(!validateMandatoryField(image_info.folder, "VM Image", modalDiv)) return false;

    // Handler to load data when received.
    var successHandler = function(vm_image) {
        $('#modal-choose-image').modal('hide');
        showImageInfoAndButtons(vm_image);

        // Notify that the process was successful.
        showAndLogSuccessMessage('Existing VM selected.');
    };

    // Do the post to get data and load the modal.
    ajaxSimplePost(actionURL, jsonData, "Selecting existing VM image", successHandler, modalDiv);

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to create a new SVM.
/////////////////////////////////////////////////////////////////////////////////////
function createSVM()
{
    // Get basic information about the form with the new svm.
    var formSVM = $('#new-svm-form');
    var serviceForm = $('#service-form');
    var actionURL = formSVM.attr('action');

    // Get all the edited fields of the svm.
    var svm_info = {};
    svm_info.source = formSVM.find('#sourceDiskImage').val();
    svm_info.type = formSVM.find('#osType').val();
    svm_info.port = serviceForm.find('#servicePort').val();
    svm_info.serviceId = serviceForm.find('#serviceID').val();
    var jsonData = JSON.stringify(svm_info);
    
    // Validate that we have all the necessary info.
    var modalDiv = $('#modal-new-servicevm');
    if(!validateMandatoryField(svm_info.serviceId, "Service Id", modalDiv)) return false;
    if(!validateMandatoryField(svm_info.port, "Service Port", modalDiv)) return false;
    if(!validateMandatoryField(svm_info.source, "VM Image", modalDiv)) return false;
    
    // Handler to load data when received.
    var successHandler = function(svm) {
        // Update the buttons to reflect that we can now save the SVM.
        showImageInfoAndButtons(svm);
        
        $('#modal-new-servicevm').modal('hide');  

        // Notify that the process was successful.
        showAndLogSuccessMessage('New VM running with id ' + svm._id + ', VNC open on port ' + svm.vnc_port);
    };
    
    // Do the post to get data and load the modal.
    ajaxSimplePost(actionURL, jsonData, "Starting and Connecting to Service VM", successHandler, modalDiv);
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start an instance to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function startInstance(url)
{
    // Send additional parameter to ensure we get a full image in the instance, not a linked qcow.
    url = url + "/" + $('#serviceID').val() + "?clone_full_image=True";
    
    // Do the post to get data and load the modal.
    ajaxGet(url, "Starting Instance to Modify SVM", function(svm) {
        // Update the buttons to reflect that we can now save the SVM.
        console.log(svm);
        showServiceVMButtons(svm);

        showAndLogSuccessMessage('Instance was started successfully with id ' + svm._id + ', VNC open on port ' + svm.vnc_port);
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to save an edited SVM.
/////////////////////////////////////////////////////////////////////////////////////
function persistInstance(url)
{
    // Add the instance ID to the URL.
    var svm_id = $('#svmInstanceId').val();
    url = url + "/" + svm_id;

    // Add para to indicate if we are creating or editing a VM here.
    var editing_SVM = $('#internalServiceId').val() != '';
    url = url + "?editing=" + editing_SVM

    // Do the post to get data and load the modal.
    ajaxGet(url, "Saving SVM", function(vm_image) {
        showImageInfoAndButtons(vm_image);

        showAndLogSuccessMessage('Changes saved successfully to permanent VM image.');
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to discard an edited SVM.
/////////////////////////////////////////////////////////////////////////////////////
function discardInstance(url)
{
    // Add the instance ID to the URL.
    var svmId = $('#svmInstanceId').val();
    url = url + "/" + svmId;

    // Do the post to get data and load the modal.
    ajaxGet(url, "Discarding SVM", function(response) {
        showAndLogSuccessMessage('Changes were discarded.');
        $('#save-svm-button').hide();
        $('#discard-svm-button').hide();
        $('#vnc-button').hide();
        $('#choose-image-button').show();

        if($('#internalServiceId').val() != '') {
            $('#modify-svm-button').show();
        }
        else {
            $('#new-svm-button').show();
        }
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Add the instance ID to the URL.
    var svmId = $('#svmInstanceId').val();
    vncUrl = vncUrl + "/" + svmId;
    
    // Handler to load data when received.
    var successHandler = function(response) {
        showAndLogSuccessMessage('VNC window was opened locally on server.');
    };
    
    // Do the post to get data and load the modal.
    ajaxGet(vncUrl, "Starting and Connecting to Service VM", successHandler);    

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Helper function.
/////////////////////////////////////////////////////////////////////////////////////
function getFileDirectory(filePath) 
{
  if (filePath.indexOf("/") == -1) { // windows
    return filePath.substring(0, filePath.lastIndexOf('\\'));
  } 
  else { // unix
    return filePath.substring(0, filePath.lastIndexOf('/'));
  }
}
