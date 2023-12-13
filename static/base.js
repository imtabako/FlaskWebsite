let topButton = document.getElementById("top-btn");
let header = document.getElementById("header");
let content = document.getElementById("content");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunc()};

let prevScrollTop = 0;
function scrollFunc() {
    const diffScroll = document.documentElement.scrollTop - prevScrollTop;
    prevScrollTop = document.documentElement.scrollTop;

    console.log(prevScrollTop);
    console.log(document.documentElement.scrollTop);

    if (document.documentElement.scrollTop == 0) {
        header.style.height = '80px';
        content.style.top = '80px';
    }

    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        topButton.style.opacity = '1';
        topButton.style.pointerEvents = 'all';
        // header.style.height = '0';
    } else {
        // topButton.style.display = "none";
        topButton.style.opacity = '0';
        topButton.style.pointerEvents = 'none';
        // header.style.height = '80px';
    }

    if (diffScroll > 0) {
        header.style.height = '0';
        // content.style.top = '0';

    } else if (diffScroll < 0) {
        header.style.height = '80px';
        // content.style.top = '80px';
    }
}

// When the user clicks on the button, scroll to the top of the document
function scroll_top() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}