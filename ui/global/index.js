

let lastPage = null

let pages = []
let currentIndex = 0

document.addEventListener("DOMContentLoaded", ()=>{
    document.querySelectorAll("[page]").forEach((el)=>{
        if (el.hasAttribute('invisible')){
            el.classList.add("invisible")
            el.removeAttribute("invisible")
        } else {
            pages.push(el.getAttribute('page'))
           currentIndex++

        }
    })
})

function goFoward(){

    currentIndex+=1
    if (currentIndex>=pages.length){
        currentIndex = pages.length - 1
    }
    goTo(pages[currentIndex])
}

function goBack() {
    if (currentIndex == pages.length){
        currentIndex -= 2
    } else {
        currentIndex -=1
    }
    if (currentIndex<0){
        currentIndex = 0
        return;
    }
    goTo(pages[currentIndex])
}

function goTo(page) {
    document.querySelectorAll("[page]").forEach((el)=>{
        const pageName = el.getAttribute('page')
        if (!el.classList.contains("invisible")){
            lastPage = pageName
        }
        if (pageName == page){
           el.classList.remove("invisible")
           pages.push(pageName)
           currentIndex++
        } else {
            el.classList.add("invisible")
        }
    })
}