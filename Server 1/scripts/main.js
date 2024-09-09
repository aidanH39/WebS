// Variables
var imageSliders = {};

// Functions
function stringGen(len) {
    var text = "";

    var charset = "abcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < len; i++)
        text += charset.charAt(Math.floor(Math.random() * charset.length));

    return text;
}

// JQuery Events

// Register these events after document has fully loaded!


function reload_image_sliders() {

    $(".image-slider").each(function () {
        // Assign unique ID to the image slider for reference later.
        var id = stringGen(15);
        console.log(this);
        this.setAttribute("id", id);
    
        var images = [];
        var c = $(this).children();
        for (var e in c) {
            if (c[e].tagName == "IMG") {
                images.push(c[e]);
            }
        }
    
        imageSliders[id] = {
            "element": this,
            "images": images
        };
    });
    
    $(".image-slider .right").click(function () {
    
        var imageSlider = imageSliders[this.parentElement.getAttribute("id")];
    
        var slider = imageSlider.element;
        var current = slider.getAttribute("current");
        var i = current;
        if (i == null) {
            i = 1;
            current = 1;
        }
        i++;
        if (i > imageSlider.images.length) {
            i = 1;
        }
    
        imageSlider.images[current - 1].classList.remove("show");
        imageSlider.images[i - 1].classList.add("show");
        slider.setAttribute("current", i);
    });
    
    $(".image-slider .left").click(function () {
    
        var imageSlider = imageSliders[this.parentElement.getAttribute("id")];
    
        var slider = imageSlider.element;
        var current = slider.getAttribute("current");
        var i = current;
        if (i == null) {
            i = 1;
            current = 1;
        }
        i--;
        if (i < 1) {
            i = imageSlider.images.length;
        }
    
        imageSlider.images[current - 1].classList.remove("show");
        imageSlider.images[i - 1].classList.add("show");
        slider.setAttribute("current", i);
    });
};

$(this).ready(function() {
    reload_image_sliders();
});
