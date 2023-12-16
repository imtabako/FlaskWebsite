tinymce.init({
    selector: '#body',
    plugins: [
        'a11ychecker','advlist','advcode','advtable','autolink','checklist','export',
        'lists','link','image','charmap','preview','anchor','searchreplace','visualblocks',
        'powerpaste','fullscreen','formatpainter','insertdatetime','media','table','help','wordcount'

    ],

    toolbar: 'undo redo | formatpainter casechange blocks | bold italic backcolor | ' +
        'alignleft aligncenter alignright alignjustify | ' +
        'bullist numlist checklist outdent indent | removeformat | a11ycheck code table help'
});

let topButton = document.getElementById("top-btn");
let header = document.getElementById("header");
let content = document.getElementById("content");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunc()};

let prevScrollTop = 0;
function scrollFunc() {
    const diffScroll = document.documentElement.scrollTop - prevScrollTop;
    prevScrollTop = document.documentElement.scrollTop;

    if (document.documentElement.scrollTop == 0) {
        // header.style.height = '80px';
        header.style.transform = 'translateY(0px)';
        // content.style.top = '80px';
    }

    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        topButton.style.opacity = '1';
        topButton.style.pointerEvents = 'all';
    } else {
        topButton.style.opacity = '0';
        topButton.style.pointerEvents = 'none';
    }

    if (diffScroll > 0) {
        // header.style.height = '0';
        header.style.transform = 'translateY(-100%)';
        // content.style.top = '0';

    } else if (diffScroll < 0) {
        // header.style.height = '80px';
        header.style.transform = 'translateY(0px)';
        // content.style.top = '80px';
    }
}

// When the user clicks on the button, scroll to the top of the document
function scroll_top() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}