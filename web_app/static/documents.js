document.querySelector('body').addEventListener('click', myFunc);

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

function myFunc(e) {
    if (e.target.className === "far fa-copy") {
        tt = e.target.parentElement
        $(tt).attr('data-original-title', 'Copied!').tooltip('show');
        $(tt).attr('data-original-title', 'Copy link to clipboard');
        link = e.target.getAttribute('value')
        saveToClipboard(link)

    } else if (e.target.className === "btn btn-light-dark") {
        tt = e.target
        $(tt).attr('data-original-title', 'Copied!').tooltip('show');
        $(tt).attr('data-original-title', 'Copy link to clipboard');
        link = tt.childNodes[1].getAttribute('value')
        saveToClipboard(link)
    } else if (e.target.className === "delete-btn") {
        let link = e.target.getAttribute('href')
        let title = e.target.parentElement.parentElement.childNodes[3].innerText;
        let msg = `<div>Are you sure to delete</div>
        <div style="font-weight:bold; text-align: center; padding:20px;">
            <span>${title}</span> ?
        </div>`
        document.getElementById('delete-modal-body').innerHTML = msg;
        document.getElementById('delete-modal-btn').setAttribute('href', link)
        $('#deleteModal').modal('show');
        e.preventDefault();
    }

}

function saveToClipboard(text) {
    var input = document.createElement('input');
    input.setAttribute('value', text);
    document.body.appendChild(input);
    input.select();
    var result = document.execCommand('copy');
    document.body.removeChild(input);
    return result;
}

window.addEventListener('load', () => {
    if ((document.querySelector('.text-danger') !== null ) | (document.querySelector('.invalid-feedback') !== null)) {
        document.getElementById('create-doc-btn').click();
    };
  });

document.getElementById('close-doc-btn').addEventListener('click', () => {
    document.getElementById('create-doc-form').reset();
    
})

document.querySelector('form').addEventListener('submit', (e) => {
    document.getElementById('btnSubmit').style.display = 'none';
    document.getElementById('btn-loading').style.display = 'block';
    document.getElementById("close-doc-btn").disabled = true;
})

document.getElementById('delete-modal-btn').addEventListener('click', (e) => {
    document.getElementById('delete-modal-btn').style.display = 'none';
    document.getElementById('btn-del-loading').style.display = 'block';
    document.getElementById("btn-cancel-del").disabled = true;
})