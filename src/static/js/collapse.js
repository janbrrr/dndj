function toggleCollapsedIcon(e) {
    $(e.target).prev(".collapse-btn").find(".collapse-icon").toggleClass("fa-plus fa-minus");
}


$(document).ready(function() {
    const collapsibles = $(".collapse");
    collapsibles.on('hidden.bs.collapse', toggleCollapsedIcon);
    collapsibles.on('shown.bs.collapse', toggleCollapsedIcon);
});