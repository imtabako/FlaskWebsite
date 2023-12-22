var phone = document.getElementById('phone');
var inn = document.getElementById('inn');
var kpp = document.getElementById('kpp');
var docs = document.getElementById('docs');

digits_only = function(e) {
    if (isNaN(e.key) &&
        e.key != 'Backspace' &&
        e.keyCode != 37 &&
        e.keyCode != 39
    ) {
        e.preventDefault();
    }
    console.log(phone.value);
}

inn.onkeydown = digits_only;
kpp.onkeydown = digits_only;

// docs attachments
function removeFile(button, fileName) {
    const fileList = document.getElementById('files-attached');

    console.log(fileList);
    console.log(docs.files);

    var updatedList = new DataTransfer();

    // Remove the corresponding file from the file input
    const fileToRemoveInd = Array.from(docs.files).findIndex(file => file.name === fileName);
    console.log(fileToRemoveInd);

    for (let i = 0; i < docs.files.length; i++) {
        if (i == fileToRemoveInd)
            continue;

        updatedList.items.add(docs.files[i]);

        console.log(docs.files[i]);
        console.log(i);
    }
    docs.files = updatedList.files;
    console.log(docs.files);

    // docs.files = new FileList([...docs.files].filter(file => file !== fileToRemove));

    // Remove the file entry from the file list
    fileList.removeChild(button.parentElement);
}

docs.onchange = function (e) {
    console.log(e);

    const fileList = document.getElementById("files-attached");
    console.log(fileList);
    console.log(docs.files);

    fileList.innerHTML = '';

    for (const file of docs.files) {
        const listItem = document.createElement('div');
        listItem.innerHTML = `<button type="button" onclick="removeFile(this, '${file.name}')"><span>${file.name}</span></button>`;
        fileList.appendChild(listItem);
    }
};


// tel validation
var keyCode;
function mask(event) {
    event.keyCode && (keyCode = event.keyCode);
    var pos = this.selectionStart;
    if (pos < 3) event.preventDefault();
    var matrix = "+7 (___) ___-____",
        i = 0,
        def = matrix.replace(/\D/g, ""),
        val = this.value.replace(/\D/g, ""),
        new_value = matrix.replace(/[_\d]/g, function(a) {
            return i < val.length ? val.charAt(i++) : a
        });
    i = new_value.indexOf("_");
    if (i != -1) {
        i < 5 && (i = 3);
        new_value = new_value.slice(0, i)
    }
    var reg = matrix.substr(0, this.value.length).replace(/_+/g,
        function(a) {
            return "\\d{1," + a.length + "}"
        }).replace(/[+()]/g, "\\$&");
    reg = new RegExp("^" + reg + "$");
    if (!reg.test(this.value) || this.value.length < 5 || keyCode > 47 && keyCode < 58) {
        this.value = new_value;
    }
    if (event.type == "blur" && this.value.length < 5) {
        this.value = "";
    }
}

phone.addEventListener("input", mask, false);
phone.addEventListener("focus", mask, false);
phone.addEventListener("blur", mask, false);
phone.addEventListener("keydown", mask, false);

// function validateInput(input) {
//     console.log('o');
//     // Remove non-digit characters
//     input.value = input.value.replace(/\D/g, '');

//     // You can add additional validation logic here if needed
// }

// inn.oninput = validateInput(inn)
// kpp.oninput = validateInput(kpp)