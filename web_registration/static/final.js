let tg = window.Telegram.WebApp
let backToBotButton = document.getElementById('back_to_bot')

backToBotButton.addEventListener('click', function() {
    // Отправка данных в бота
    let data = {status: 'ok'}

    tg.sendData(JSON.stringify(data));

    // Закрытие веб-приложения с регистрацией
    tg.close();
})