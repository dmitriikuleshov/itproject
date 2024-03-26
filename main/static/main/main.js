document.getElementById('close').addEventListener('click', function () {
    document.getElementById('sidebar').style.display = 'none';
    document.body.style.marginLeft = '60px';
})

document.getElementById('open-bar').addEventListener('click', function () {
    document.getElementById('sidebar').style.display = 'inline';
    document.body.style.marginLeft = '280px';
})