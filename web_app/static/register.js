// async function main() {
//     try {
//         await liff.init({ liffId: "1656236254-w6xkRkYK" })
//     }  catch {

//     }
    
//     try {
//         document.getElementById("userIDToken").value = (liff.getIDToken())
//         console.log(liff.getIDToken())
//     } catch {
//         alert("Failed to get IdToken")
//     }
//   }



document.getElementById('submit').addEventListener('click',(e) => {
    if(document.getElementById('dealer').value === "เลือกศูนย์บริการ") {
        alert('โปรดเลือกศูนย์บริการของท่าน');
        e.preventDefault();
    } else if (document.getElementById('position').value === "เลือกตำแหน่งงาน" && document.getElementById('dealer').value !== "TIS group") {
        alert('โปรดเลือกตำแหน่งงานของท่าน');
        e.preventDefault();
    }

});

dealer = document.getElementById('dealer')
position = document.getElementById('form-position')

dealer.addEventListener('change', () => {
    if(dealer.value !== "TIS group") {
        position.style.display = "block";
    } else {
        position.style.display = "none";
    }
})



document.querySelector("#position").firstElementChild.disabled = true;
document.querySelector("#dealer").firstElementChild.disabled = true;

