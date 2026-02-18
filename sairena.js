function setMode(mode){
    fetch("/set_mode", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({mode:mode})
    });
}

function sendMessage(){
    let message = document.getElementById("message").value;
    fetch("/chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:message})
    })
    .then(res=>res.json())
    .then(data=>{
        let chat = document.getElementById("chat");
        chat.innerHTML += "<p><b>Вы:</b> "+message+"</p>";
        chat.innerHTML += "<p><b>Рена:</b> "+data.response+"</p>";
        chat.scrollTop = chat.scrollHeight;
    });
    document.getElementById("message").value="";
}

function setMood(){
    let mood_val = document.getElementById("mood").value;
    fetch("/mood", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({mood:mood_val})
    });
    alert("Настроение сохранено!");
}
