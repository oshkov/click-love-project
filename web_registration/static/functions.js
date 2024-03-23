// Предпросмотр фото и проверка на размер файла
function preview(MAX_MB_SIZE, MAX_PHOTO_AMOUNT) {
    let inputPhotos = document.getElementById('photo_input')    // Input из html
    let amountPhotos = inputPhotos.files.length                 // Общее количество фото

    // Очистка от старых фото
    let previewImgsBlock = document.getElementById('preview_imgs')
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
                return
            }
            
            htmlBlock = `
            <div class="image_block" id="image_block${num}">
                <img src="${URL.createObjectURL(photo)}">
            </div>
            `

            preview_imgs.insertAdjacentHTML('afterbegin', htmlBlock);
            num += 1
        }

        document.getElementById('input-file-btn').textContent = 'Выбрать другие фото'

    } else {
        alert(`Нельзя загружать более ${MAX_PHOTO_AMOUNT} фото!`)
        inputPhotos.value = ''                  // Очистка инпута
        previewImgsBlock.innerHTML = ''         // Очистка блока с предпросмотром фото
    }
}


let citySelected = false        // Переменная для показа, что город был выбран из списка предложенного

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