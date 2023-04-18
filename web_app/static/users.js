document.querySelector('tbody').addEventListener('click', confirmAction);

let action;
let row;
let name;
let surname;
let url;

function confirmAction (e) {
    if (e.target.classList.contains("dropdown-item")){
        action = e.target.innerText.toLowerCase();
        url = e.target.getAttribute('href');
        row = e.target.parentNode.parentNode.parentNode.parentNode.
        children;
        name = row[1].innerText;
        surname = row[2].innerText;

        document.querySelector(".modal-title").innerText = "Confirm";

        let btnClass;
        if (action === 'block') {
            btnClass = "btn btn-danger";
        }
        if (action === 'delete') {
            btnClass = "btn btn-danger";
        }
        if (action === 'approve') {
            btnClass = 'btn btn-success';
        }
        if (action === 'reject') {
            btnClass = 'btn btn-dark';
        }
        if (action === 'unblock') {
            btnClass = 'btn btn-info';
        }
        let msg = `<div>Are you sure to <span>${action}</span></div>
        <div style="font-weight:bold; text-align: center; padding:20px;">
            <span>${name}</span> ${surname} ?
        </div>`

        if(action === 'delete') {
            msg = msg + "<div style='color:red'>This action cannot be restored</div>"
        }

        document.querySelector(".modal-body").innerHTML = msg;
        document.getElementById('modal-btn').setAttribute('href', url);
        document.getElementById('modal-btn').className = btnClass;
        document.getElementById('btn-loading').className = btnClass;
        document.getElementById('modal-btn').innerHTML = e.target.innerText
        e.preventDefault();
    }
}

document.getElementById('modal-btn').addEventListener('click', (e) => {
    document.getElementById('modal-btn').style.display = 'none';
    document.getElementById('btn-loading').style.display = 'block';
    document.getElementById("modal-cancel-btn").disabled = true;
})


