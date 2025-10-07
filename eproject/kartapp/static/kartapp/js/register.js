let eye_btn1 = document.querySelector('.eye1')
let pwinput1 = document.querySelector('.pw1')
let show_password = document.querySelector('#id_password1')

let eye_btn2 = document.querySelector('.eye2')
let pwinput2 = document.querySelector('.pw2')
let show_password2 = document.querySelector('#id_password2')

pwinput1.addEventListener('click',()=>{
    if (eye_btn1.classList.contains('fa-eye')) {
        eye_btn1.classList.replace("fa-eye","fa-eye-slash")
        show_password.type = "text"
            
    }
    else{
        eye_btn1.classList.replace("fa-eye-slash","fa-eye")
        show_password.type = "password"
    }
})

pwinput2.addEventListener('click',()=>{
    if (eye_btn2.classList.contains('fa-eye')) {
        eye_btn2.classList.replace("fa-eye","fa-eye-slash")
        show_password2.type = "text"
            
    }
    else{
        eye_btn2.classList.replace("fa-eye-slash","fa-eye")
        show_password2.type = "password"
    }
})