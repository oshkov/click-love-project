// Предпросмотр фото после выбора и проверка на размер фото
let photoInputMain = document.getElementById('photo_input_main')
photoInputMain.addEventListener('change', () => preview(MAX_MB_PHOTO_SIZE, MAX_PHOTO_AMOUNT, 'main'))
let photoInputMore = document.getElementById('photo_input_more')
photoInputMore.addEventListener('change', () => preview(MAX_MB_PHOTO_SIZE, MAX_PHOTO_AMOUNT, 'more'))


// Убирается ошибка при вводе данных
let inputUsername = document.getElementById('username_input')
inputUsername.addEventListener('input', function () {
    inputUsername.style = 'border: none'
    document.getElementById('error_username').textContent = ''
})

// Переход от запроса имени к запросу возраста
let continueUsername = document.getElementById('continue_username')
continueUsername.addEventListener('click', function() {
    // Проверка на ввод имени
    if (inputUsername.value === '') {
        document.getElementById('error_username').textContent = 'Это обязательное поле'
        inputUsername.style = 'border: 2px solid red'
        return
    } else if (inputUsername.value.includes('http')) {
        document.getElementById('error_username').textContent = 'Введите свое имя, а не ссылку'
        inputUsername.style = 'border: 2px solid red'
        return
    } else if (inputUsername.value.includes('.')) {
        document.getElementById('error_username').textContent = 'Введите свое имя'
        inputUsername.style = 'border: 2px solid red'
        return
    }

    // Переход на следующий вопрос
    document.getElementById('username_form').style.display = 'none'
    document.getElementById('age_form').style.display = 'block'
})


// Убирается ошибка при вводе данных
let inputAge = document.getElementById('age_input')
inputAge.addEventListener('input', function () {
    inputAge.style = 'border: none'
    document.getElementById('error_age').textContent = ''
})

// Переход от запроса возраста к запросу гендера
let continueAge = document.getElementById('continue_age')
continueAge.addEventListener('click', function() {
    // Проверка на ввод возраста
    if (inputAge.value === '') {
        document.getElementById('error_age').textContent = 'Это обязательное поле'
        inputAge.style = 'border: 2px solid red'
        return
    } else if (inputAge.value < 18) {
        document.getElementById('error_age').textContent = 'Минимальный возраст 18 лет'
        inputAge.style = 'border: 2px solid red'
        return
    } else if (inputAge.value > 80) {
        document.getElementById('error_age').textContent = 'Максимальный возраст 80 лет'
        inputAge.style = 'border: 2px solid red'
        return
    }

    // Переход на следующий вопрос
    document.getElementById('age_form').style.display = 'none'
    document.getElementById('gender_form').style.display = 'block'
})


// Убирается ошибка при вводе данных
let inputGenderMale = document.getElementById('input_male')
let inputGenderFemale = document.getElementById('input_female')
inputGenderMale.addEventListener('change', function () {
    document.getElementById('error_gender').textContent = ''
})
inputGenderFemale.addEventListener('change', function () {
    document.getElementById('error_gender').textContent = ''
})

// Переход от запроса гендера к запросу города
let continueGender = document.getElementById('continue_gender')
continueGender.addEventListener('click', function() {
    // Проверка на выбор пола
    if (inputGenderMale.checked === false && inputGenderFemale.checked === false) {
        document.getElementById('error_gender').textContent = 'Укажите свой пол'
        return
    }

    // Переход на следующий вопрос
    document.getElementById('gender_form').style.display = 'none'
    document.getElementById('city_form').style.display = 'block'
})


// Убирается ошибка при вводе данных
let inputCity = document.getElementById('city_input')
inputCity.addEventListener('input', function () {
    inputCity.style = 'border: none'
    document.getElementById('error_city').textContent = ''
})

// Переход от запроса города к запросу предпочтений
let continueCity = document.getElementById('continue_city')
continueCity.addEventListener('click', function() {
    if (citySelected === false) {
        document.getElementById('error_city').textContent = 'Выберите город из предложенных'
        inputCity.style = 'border: 2px solid red'
        return
    }

    // Переход на следующий вопрос
    document.getElementById('city_form').style.display = 'none'
    document.getElementById('preferences_form').style.display = 'block'
})


// Убирается ошибка при вводе данных
let inputPreferMale = document.getElementById('input_with_male')
let inputPreferFemale = document.getElementById('input_with_female')
let inputPreferEveryone = document.getElementById('input_with_everyone')
inputPreferMale.addEventListener('change', function () {
    document.getElementById('error_prefer').textContent = ''
})
inputPreferFemale.addEventListener('change', function () {
    document.getElementById('error_prefer').textContent = ''
})
inputPreferEveryone.addEventListener('change', function () {
    document.getElementById('error_prefer').textContent = ''
})

// Переход от запроса предпочтений к запросу целей
let continuePreferences = document.getElementById('continue_preferences')
continuePreferences.addEventListener('click', function() {
    // Проверка на выбор предпочтений
    if (inputPreferMale.checked === false && inputPreferFemale.checked === false && inputPreferEveryone.checked === false) {
        document.getElementById('error_prefer').textContent = 'Укажите предпочтения'
        return
    }

    document.getElementById('preferences_form').style.display = 'none'
    document.getElementById('target_form').style.display = 'block'
})


// Переход от запроса целей к запросу О себе
let continueTarget = document.getElementById('continue_target')
continueTarget.addEventListener('click', function() {
    // Переход на следующий вопрос
    document.getElementById('target_form').style.display = 'none'
    document.getElementById('photo_form').style.display = 'block'
})


// Переход от запроса целей к запросу О себе
let inputPhotosMain = document.getElementById('photo_input_main')
let photosMoreBlock = document.getElementById('more_photo_block')

inputPhotosMain.addEventListener('change', function () {
    if (inputPhotosMain.value === '') {
        photosMoreBlock.style.display = 'none'
    } else {
        photosMoreBlock.style.display = 'block'
    }
})

let continuePhoto = document.getElementById('continue_photo')
continuePhoto.addEventListener('click', function() {
    // Проверка на наличие фото
    if (inputPhotosMain.value === '') {
        document.getElementById('error_photo').textContent = 'Необходимо загрузить фото'
        return
    }

    // Переход на следующий вопрос
    document.getElementById('photo_form').style.display = 'none'
    document.getElementById('about_form').style.display = 'block'
})


// Обработка нажатия на кнопку регистрации
let registrateButton = document.getElementById('registrate')
registrateButton.addEventListener('click', function() {
    // Проверка на принятие соглашения
    let inputAgreement = document.getElementById('agreement')
    if (inputAgreement.checked === false) {
        document.getElementById('error_agreement').textContent = 'Для регистрации необходимо принять соглашение'
        return
    }

    // Вывод загрузки
    document.getElementById('about_form').style.display = 'none'
    document.getElementById('loading').style.display = 'block'
    document.getElementById('logo_h2').textContent = 'Создание анкеты'

    // Отмена отправки формы по умолчанию
    event.preventDefault()

    // Отправка формы
    let form = document.getElementById('form')
    form.submit()
})