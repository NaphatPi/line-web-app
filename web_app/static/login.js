async function main () {
  document.getElementById("getOS").value = liff.getOS();
  document.getElementById("isInClient").value = liff.isInClient();
  
  try{
    await liff.init({ liffId: liffId })
    document.getElementById("userIDToken").value = liff.getIDToken()
    console.log('init success')
  } catch (e) {
    console.log('init fail')
  }

  try {
    friend = await liff.getFriendship()
    document.getElementById("getFriendShip").value = friend["friendFlag"]
    document.getElementById("getFriendShip").value
  } catch (e) {
    console.log('friendship fail')
  }

  document.getElementById('login').submit()
}

let liffId = document.getElementById('liffId').innerText;

main()