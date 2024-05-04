let inputCity = document.getElementById('city_input')
let citySelected = true        // Переменная для показа, что город был выбран из списка предложенного

function formatSelected(suggestion) {
	return suggestion.data.city;
}

$("#city_input").suggestions({
	token: "18ce8e4f8a4137e861beef9cef2ad278ebf7425a",
	type: "ADDRESS",
	hint: false,
	bounds: "city",
  	formatSelected: formatSelected,
	constraints: {
		locations: {country: "*"}
	},
	// Вызывается, когда пользователь выбирает одну из подсказок
	onSelect: function(suggestion) {
        citySelected = true
		// console.log(suggestion.data.city);
		// console.log(citySelected);

        // Убирается ошибка, если она была
        inputCity.style = 'border: none'
        document.getElementById('error_city').textContent = ''
	}
});
$("#city_input").attr("autocomplete", "off");

// При изменении строки ввода города, переменная citySelected изменяется на false
inputCity.addEventListener("input", function() {
    citySelected = false
    // console.log(citySelected);
})


// Предпросмотр фото после выбора и проверка на размер фото
let photoInputMain = document.getElementById('photo_input_main')
photoInputMain.addEventListener('change', () => preview(MAX_MB_PHOTO_SIZE, MAX_PHOTO_AMOUNT, 'main'))
let photoInputMore = document.getElementById('photo_input_more')
photoInputMore.addEventListener('change', () => preview(MAX_MB_PHOTO_SIZE, MAX_PHOTO_AMOUNT, 'more'))

// Предпросмотр фото и проверка на размер файла
function preview(MAX_MB_SIZE, MAX_PHOTO_AMOUNT, type) {
    let inputPhotos                 // Input из html
    let previewImgsBlock
    if (type === 'main') {
        inputPhotos = document.getElementById('photo_input_main')
        previewImgsBlock = document.getElementById('preview_imgs_main')
    } else {
        inputPhotos = document.getElementById('photo_input_more')
        previewImgsBlock = document.getElementById('preview_imgs_more')
    }

    let amountPhotos = inputPhotos.files.length                 // Общее количество фото

    // Очистка от старых фото
    previewImgsBlock.innerHTML = ''                      // Очистка блока с предпросмотром фото

    // Проверка на количество фото
    if (amountPhotos <= MAX_PHOTO_AMOUNT) {

        // Вывод фото в html
        num = 0
        while (amountPhotos > num) {
            photo = inputPhotos.files[num]

            // Проверка фото на размер, если размер больше MAX_MB_SIZE, то все фото отменяются
            if (photo.size > MAX_MB_SIZE * 1024 * 1024) {
                inputPhotos.value = ''                               // Очистка инпута
                previewImgsBlock.innerHTML = ''                      // Очистка блока с предпросмотром фото
                alert(`Размер фото не должен превышать ${MAX_MB_SIZE}мб!\n\n${photo.name} превышает допустимый размер для загрузки!`)
                document.getElementById('input-file-btn').textContent = 'Выбрать фото'
                return
            }

            htmlBlock = `
            <div class="image_block" id="image_block${num}">
                <img src="${URL.createObjectURL(photo)}" name="${photo.name}">
            </div>
            `

            previewImgsBlock.insertAdjacentHTML('afterbegin', htmlBlock);
            num += 1
        }

    } else {
        alert(`Нельзя загружать более ${MAX_PHOTO_AMOUNT} фото!`)
        inputPhotos.value = ''                  // Очистка инпута
        previewImgsBlock.innerHTML = ''         // Очистка блока с предпросмотром фото
    }
}


// Убирается ошибка при вводе данных
let inputAge = document.getElementById('age_input')
inputAge.addEventListener('input', function () {
    inputAge.style = 'border: none'
    document.getElementById('error_age').textContent = ''
})

// Убирается ошибка при вводе данных
inputCity.addEventListener('input', function () {
    inputCity.style = 'border: none'
    document.getElementById('error_city').textContent = ''
})

// Обработка нажатия на кнопку регистрации
let editProfileButton = document.getElementById('edit_profile')
editProfileButton.addEventListener('click', function() {
    // Проверка на возраст
    if (inputAge.value === '') {
        document.getElementById('error_age').textContent = 'Это обязательное поле'
        inputAge.style = 'border: 2px solid red'
        inputAge.scrollIntoView({ block: "center", behavior: "smooth" });
        return
    } else if (inputAge.value < 18) {
        document.getElementById('error_age').textContent = 'Минимальный возраст 18 лет'
        inputAge.style = 'border: 2px solid red'
        inputAge.scrollIntoView({ block: "center", behavior: "smooth" });
        return
    } else if (inputAge.value > 80) {
        document.getElementById('error_age').textContent = 'Максимальный возраст 80 лет'
        inputAge.style = 'border: 2px solid red'
        inputAge.scrollIntoView({ block: "center", behavior: "smooth" });
        return
    }
    // Проверка на выбор города
    if (citySelected === false) {
        document.getElementById('error_city').textContent = 'Выберите город из предложенных'
        inputCity.style = 'border: 2px solid red'
        inputCity.scrollIntoView({ block: "center", behavior: "smooth" });
        return
    }
    // Проверка на принятие соглашения
    let inputAgreement = document.getElementById('agreement')
    if (inputAgreement.checked === false) {
        document.getElementById('error_agreement').textContent = 'Для регистрации необходимо принять соглашение'
        return
    }

    // Вывод загрузки
    document.getElementById('username_form').style.display = 'none'
    document.getElementById('age_form').style.display = 'none'
    document.getElementById('gender_form').style.display = 'none'
    document.getElementById('city_form').style.display = 'none'
    document.getElementById('preferences_form').style.display = 'none'
    document.getElementById('target_form').style.display = 'none'
    document.getElementById('photo_form').style.display = 'none'
    document.getElementById('about_form').style.display = 'none'
    document.getElementById('edit_profile').style.display = 'none'
    document.getElementById('loading').style.display = 'block'
    document.getElementById('logo_h2').textContent = 'Редактирование анкеты'

    // Отмена отправки формы по умолчанию
    event.preventDefault()

    // Отправка формы
    let form = document.getElementById('form')
    form.submit()
})