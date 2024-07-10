$(document).ready(function() {
    // Restore sidebar state
    if (localStorage.getItem('sidebarState') === 'shown') {
        $('#sidebar').addClass('show');
        $('#content').addClass('shift');
    }

    // Restore active category and subcategory states
    if (localStorage.getItem('activeCategory')) {
        $('#' + localStorage.getItem('activeCategory')).addClass('active');
    }
    if (localStorage.getItem('subcategoryState')) {
        let subcategoryState = JSON.parse(localStorage.getItem('subcategoryState'));
        for (let key in subcategoryState) {
            if (subcategoryState[key]) {
                $('#' + key).next('.subcategory-list').addClass('show');
            }
        }
    }

    // Show sidebar and content after setting state
    setTimeout(function() {
        $('#sidebar').addClass('show');
        $('#content').addClass('visible');
    }, 100); // Slight delay to ensure JS processes state changes

    // Toggle sidebar visibility
    $('#sidebarToggle').on('click', function() {
        $('#sidebar').toggleClass('show');
        $('#content').toggleClass('shift');
        localStorage.setItem('sidebarState', $('#sidebar').hasClass('show') ? 'shown' : 'hidden');
    });

    // Handle category click
    $('.category-item').on('click', function(e) {
        e.preventDefault();
        $(this).next('.subcategory-list').toggleClass('show');
        $('.category-item').removeClass('active');
        $(this).addClass('active');
        localStorage.setItem('activeCategory', $(this).attr('id'));
        localStorage.setItem('subcategoryState', JSON.stringify(getSubcategoryStates()));
    });

    function getSubcategoryStates() {
        let states = {};
        $('.category-item').each(function() {
            let subcategoryList = $(this).next('.subcategory-list');
            states[$(this).attr('id')] = subcategoryList.hasClass('show');
        });
        return states;
    }
});

window.onload = function() {
    document.getElementById('sidebar').style.visibility = 'visible';
    document.getElementById('content').style.visibility = 'visible';
};