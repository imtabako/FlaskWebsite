tinymce.init({
    selector: '#body',
    plugins: [
        'a11ychecker','advlist','advcode','advtable','autolink','checklist','export',
        'lists','link','image','charmap','preview','anchor','searchreplace','visualblocks',
        'powerpaste','fullscreen','formatpainter','insertdatetime','media','table','help','wordcount'

    ],

    toolbar: 'undo redo | formatpainter casechange blocks | bold italic underline backcolor | ' +
        'alignleft aligncenter alignright alignjustify | ' +
        'bullist numlist checklist outdent indent | removeformat | a11ycheck code table help',

    image_upload_url: '/upload_image',
    images_upload_base_path: '/static/uploads',
    images_upload_credentials: true
});

tinymce.activeEditor.uploadImages(function(success) {
    document.forms[0].submit();
});