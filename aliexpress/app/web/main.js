"use strict"

// カテゴリ

let categories = []
let sub_categories = []
const category_select = $('#category')
const sub_category_select = $('#sub-category')
const current_url = $('#current-url')

// class Category {
//     constructor(name, url, sub) {
//         this.name = name
//         this.url = url
//         this.sub = sub
//     }

//     add_select_option(index) {
//         const option = $('<option>').text(this.name).val(index)
//         category_select.append(option)
//     }

// }

class Category {
    constructor(name, url) {
        this.name = name
        this.url = url
    }

    add_select_option() {
        const option = $('<option>').text(this.name).val(this.url)
        category_select.append(option)
    }

}

class SubCategory {
    constructor(name, url) {
        this.name = name
        this.url = url
    }

    add_select_option() {
        const option = $('<option>').text(this.name).val(this.url)
        sub_category_select.append(option)
    }

}


// // アプリ起動時カテゴリ情報取得
// $(function() {
//     eel.searchCategory()
// })

// // 取得したカテゴリ情報をクラスにして、ドロップダウンに設定
// eel.expose(set_category)
// function set_category(category_info) {
//     categories = []
//     category_select.empty()
//     category_info.forEach((element, index) => {
//         const category = new Category(element.name, element.url, element.sub)
//         category.add_select_option(index)
//         categories.push(category)
//     })

//     add_select_option_sub(0)
// }

// // サブカテゴリのドロップダウン設定
// const add_select_option_sub = (index) => {
//     sub_category_select.empty()
//     const sub_categories = categories[index].sub
//     let option = $('<option>').text('全て').val(categories[index].url)
//     sub_category_select.append(option)

//     sub_categories.forEach(element => {
//         option = $('<option>').text(element.name).val(element.url)
//         sub_category_select.append(option)
//     })

//     set_search_url()
// }

// // ドロップダウンの設定が変更された場合に検索URLを更新
// category_select.change(function() {
//     add_select_option_sub(category_select.val())
//     set_search_url()
// })

// sub_category_select.change(function() {
//     set_search_url()
// })

// const set_search_url = () => {
//     const url = sub_category_select.val()
//     search_url.text(url).attr('onclick', `window.open('${url}')`);
// }


// 検索
$('#search').click(() => {

    const keyword = $('#keyword').val()
    // const starNumber = $('#star').val()
    // const salesNumber = $('#sales-number').val()
    // const stockNumber = $('#stock-number').val()
    // const priceLower = $('#price-lower').val()
    // const priceUpper = $('#price-upper').val()
    // const fetchNumber = $('#fetch-number').val()

    // const search_condition = {
    //     keyword: keyword,
    //     url: search_url.text(),
    //     starNumber: starNumber,
    //     salesNumber: salesNumber,
    //     stockNumber: stockNumber,
    //     priceLower: priceLower,
    //     priceUpper: priceUpper,
    //     fetchNumber: fetchNumber,
    // }

    alert('検索中・・・', 'warning')
    eel.search(keyword)

})

// 現在のURL表示
eel.expose(view_current_url)
function view_current_url(url) {

    current_url.text(url).attr('onclick', `window.open('${url}')`)

}


// カテゴリ設定
eel.expose(set_category_info)
function set_category_info(category_info) {

    categories = []
    category_select.empty()
    category_info.forEach((element) => {
        const category = new Category(element.name, element.url)
        category.add_select_option()
        categories.push(category)
    })

}

// カテゴリ絞り込み
$('#narrow-category').click(() => {

    const category_url = category_select.val()
    alert('絞り込み中・・・', 'warning')
    eel.narrow_category(category_url)

})


// サブカテゴリ設定
eel.expose(set_sub_category_info)
function set_sub_category_info(sub_category_info) {

    sub_categories = []
    sub_category_select.empty()
    sub_category_info.forEach((element) => {
        const category = new SubCategory(element.name, element.url)
        category.add_select_option()
        sub_categories.push(category)
    })

}

// サブカテゴリ絞り込み
$('#narrow-sub-category').click(() => {

    const category_url = sub_category_select.val()
    alert('絞り込み中・・・', 'warning')
    eel.narrow_category(category_url, true)

})

// 価格範囲絞り込み
$('#narrow-price-range').click(() => {

    const price_range = {
        priceLower: $('#price-lower').val(),
        priceUpper: $('#price-upper').val()
    }
    alert('絞り込み中・・・', 'warning')
    eel.narrow_price_range(price_range)

})

// 抽出
$('#fetch').click(() => {

    // const starNumber = $('#star').val()
    // const salesNumber = $('#sales-number').val()
    // const stockNumber = $('#stock-number').val()
    // const fetchNumber = $('#fetch-number').val()

    // const fetch_condition = {
    //     starNumber: starNumber,
    //     salesNumber: salesNumber,
    //     stockNumber: stockNumber,
        // fetchNumber: fetchNumber,
    // }

    alert('抽出中・・・', 'warning')
    eel.fetch()

})


let items = []
const fetch_tbody = $('#fetch-tbody')

// 抽出データクラス
class Item {
    constructor(id, title, price, url) {
        this.id = id
        this.title = title
        this.price = price
        this.url = url
    }

    view() {

        const tr = $('<tr>')
        const td_id = $('<td>').text(this.id)
        const td_title = $('<td>').text(this.title).addClass('abridgement')
        const td_price = $('<td>').text(this.price)
        const td_url = $('<td>').addClass('abridgement')
        const td_a = $('<a>').text(this.url).attr('onclick', `window.open('${this.url}')`)

        td_url.append(td_a)
        tr.append(td_id).append(td_title).append(td_price).append(td_url)
        fetch_tbody.append(tr)

    }
}

// 抽出情報表示
eel.expose(view_item_info)
function view_item_info(item_info) {

    console.log(item_info)

    items = []
    fetch_tbody.empty()
    item_info.forEach((element, index) => {
        const item = new Item(index+1, element.title, element.price, element.url)
        item.view()
        items.push(item)
    })

    $('#save').prop('disabled', false)

}

// CSV保存
$('#save').click(() => {

    const fileName = $('#file-name').val()
    eel.save(fileName)

})


// メッセージ、アラーム設定
const alert = (message, message_color) => {

    const alert = $('<div>').text(message).addClass(`alert alert-${message_color} vanish`).attr('role', 'alert').hide()
    $('#message').empty()
    $('#message').append(alert)
    alert.fadeIn(500)
}

// メッセージ、アラーム表示
eel.expose(message)
function message(message, isError=false, isWarning=false) {

    let message_color

    if (isError) {
        message_color = 'danger'
        console.error(message)
    } else if (isWarning) {
        message_color = 'warning'
        console.log(message)
    } else {
        message_color = 'success'
        console.log(message)
    }

    alert(message, message_color)

}

// メッセージ、アラームをクリックすると消えるようにする設定
$('body').on('click', '.vanish', function() {
    $(this).remove()
})


// // Seleniumドライバ設定及び検索
// $('#search').click(() => {

//     const keyword = $('#keyword').val()
//     const isSale = $('#isSale').prop('checked')
//     const priceLower = $('#price-lower').val()
//     const priceUpper = $('#price-upper').val()

//     const searchInfo = {
//         keyword: keyword,
//         isSale: isSale,
//         priceLower: priceLower,
//         priceUpper: priceUpper,
//     }
//     alert('Seleniumドライバ設定中・・・', 'warning')
//     eel.search(searchInfo)

// })

// // 情報抽出
// $('#fetch').click(() => {

//     const fetchNumber = Number($('#fetch-number').val())
//     alert('情報取得中・・・', 'warning')
//     eel.fetch(fetchNumber)

// })

// // CSV保存
// $('#save').click(() => {

//     const fileName = $('#file-name').val()
//     eel.save(fileName)

// })

// const alert = (message, message_color) => {

//     const alert = $('<div>').text(message).addClass(`alert alert-${message_color} vanish`).attr('role', 'alert').hide()
//     $('#message').empty()
//     $('#message').append(alert)
//     alert.fadeIn(500)
// }


// // 抽出ボタンENA
// eel.expose(fetch_enable)
// function fetch_enable() {
//     $('#fetch').prop('disabled', false)
// }

// // 保存ボタンENA
// eel.expose(save_enable)
// function save_enable() {
//     $('#save').prop('disabled', false)
// }


// // 抽出データのクラス化、テーブル表示
// eel.expose(viewInfo)
// function viewInfo(item_info) {

//     items = []
//     const keys = Object.keys(item_info)
//     const fetchNumber = item_info[keys[0]].length
//     const formatter = new Intl.NumberFormat('ja', {
//         style: 'currency',
//         currency: 'JPY'  
//     })

//     for (let i = 0; i < fetchNumber; i++) {
//         const name = item_info.name[i]
//         const price = formatter.format(item_info.price[i])
//         const access = item_info.access[i]
//         const like = item_info.like[i]
//         const category1 = item_info.category1[i]
//         const category2 = item_info.category2[i]
//         const category3 = item_info.category3[i]
//         items.push(new Item(i+1, name, price, access, like, category1, category2, category3))
//     }

//     fetch_tbody.empty()

//     items.forEach(item => {
//         item.view()
//     })

// }


// // タブ型ナビゲーション設定
// let tabs = $('.nav-link')
// $('.nav-link').on('click', function() {
//     $('.active').removeClass('active')
//     $(this).addClass('active')
//     const index = tabs.index(this)
//     $('.content').removeClass('show').eq(index).addClass('show')
// })
