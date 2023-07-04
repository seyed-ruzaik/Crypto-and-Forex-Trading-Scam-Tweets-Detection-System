// const api = 'http://127.0.0.1:5000/predict'
const api = 'http://3.135.190.128:5000/predict' //AWS Server

const barCount = 50;
let val;
function getCurrentTabUrl(callback) {
    var queryInfo = {
        active: true,
        currentWindow: true
    };

    chrome.tabs.query(queryInfo, function(tabs) {
        var tab = tabs[0];
        var url = tab.url;
        callback(url);
    });
}

function renderURL(statusText) {
    document.getElementById('progress').textContent = statusText;
}

document.addEventListener('DOMContentLoaded', async function() {
    getCurrentTabUrl(async function (url) {
        if (url.indexOf("status") > -1) {
            console.log("Current Tab URL",url);
            let tweetID = url.toString();
            let newTweetID = tweetID.match('(\\d+)$')
            console.log(newTweetID[0])
            let tweetData = {"Tweet_ID": newTweetID[0]}
            // Post the payload using Fetch:
            fetch(api, {
                method: 'POST',
                body: JSON.stringify(tweetData),
            }).then(function (response) {
                return response.json();
            }).then(function (text) {
                console.log(text.message);
                val = text.percentage;
                if (text.type === 'nscam'){
                    const wrapper = document.querySelectorAll('.progress');
                    const percent1 = 50 * val/100;
                    console.log(val)
                    for (let index = 0; index < barCount; index++) {
                        const className = index <= percent1 ? 'selected1' : '';
                        wrapper[0].innerHTML += `<i style="--i: ${index};" class="${className}"></i>`;
                    }

                    wrapper[0].innerHTML += `<p class="selected percent-text text1">${val}%</p>`
                    renderURL(text.message);
                } else if (text.type === 'scam'){
                    const wrapper = document.querySelectorAll('.progress');
                    const percent1 = 50 * val/100;
                    console.log(val)
                    for (let index = 0; index < barCount; index++) {
                        const className = index <= percent1 ? 'selected3' : '';
                        wrapper[0].innerHTML += `<i style="--i: ${index};" class="${className}"></i>`;
                    }

                    wrapper[0].innerHTML += `<p class="selected percent-text text3">${val}%</p>`
                    renderURL(text.message);
                } else {
                    const wrapper = document.querySelectorAll('.progress');
                    const percent1 = 50 * val/100;
                    console.log(val)
                    for (let index = 0; index < barCount; index++) {
                        const className = index <= percent1 ? 'selected2' : '';
                        wrapper[0].innerHTML += `<i style="--i: ${index};" class="${className}"></i>`;
                    }

                    wrapper[0].innerHTML += `<p class="selected percent-text text2">${val}%</p>`
                    renderURL(text.message);
                }

            });
        } else {
            val = 0;
            const wrapper = document.querySelectorAll('.progress');
            const percent1 = 50 * val/100;
            console.log(val)
            for (let index = 0; index < barCount; index++) {
                const className = index <= percent1 ? 'selected2' : '';
                wrapper[0].innerHTML += `<i style="--i: ${index};" class="${className}"></i>`;
            }

            wrapper[0].innerHTML += `<p class="selected percent-text text2">${val}%</p>`
            // The URL is outside of Twitter
            renderURL("Tweet not detected");
        }


    });

});



