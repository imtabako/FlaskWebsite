tinymce.init({
    selector: '#body',
    language: 'ru',
    plugins: 'image',
    menubar: false,
    toolbar: 'undo redo | styles | bold italic | link image | alignleft aligncenter alignright',
    relative_urls: false,
    images_upload_url: '/upload_image',
    setup: function (editor) {
        editor.on('submit', function (e) {
            editor.save();
        });
    }
});

window.onload = function() {
    var form = document.theForm;

    form.onsubmit = function() {
        tinymce.activeEditor.uploadImages().then(() => {
            form.submit();
        });
    }
}