function search_button() {
    var term = $('#txtPfam').val();
    if(term.length > 0){
        window.location.href = window.location.origin + "/search/" + term;
    }
}