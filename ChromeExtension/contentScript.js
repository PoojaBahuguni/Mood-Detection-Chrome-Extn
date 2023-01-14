var allTweets = []
var englishTweets = []
var emojiEmotionMap = {
    NEUTRAL: String.fromCodePoint(0x1F610),
    NEGATIVE: String.fromCodePoint(0x1F641),
    POSITIVE: String.fromCodePoint(0x1F60A)
};

// Getting All The Tweets From the Twitter Web Page
document.querySelectorAll('[data-testid="tweetText"]').forEach(async (index) => {
    console.log(index.textContent);
    allTweets.push({ "tweet_text": index.textContent })
});


async function addEmojis() {
    //Getting the english texts from Language Detection API1
    const response = await fetch('http://34.125.24.7:50000/api/language-detection', {
        "method": "POST",
        "body": JSON.stringify(allTweets),
        "headers": {
            'Content-Type': 'application/json'
        },
        "referrerPolicy" : "origin" 
    });

    response.json().then(async (data) => {
        data.forEach((index) => {
            if (index["is_english"]) {
                englishTweets.push({ "tweet_text": index["tweet_text"] })
            }
        })
        //Sending the English Texts to Sentiment Acore API2
        const response2 = await fetch('http://34.125.24.7:50000/api/sentiment-score', {
            "method": "POST",
            "body": JSON.stringify(data),
            "headers": {
                'Content-Type': 'application/json'
            },
            "referrerPolicy" : "unsafe_url" 
        });
        response2.json().then((data2) => {
            var userNames = document.querySelectorAll('[data-testid="User-Names"]');
            userNames.forEach((userNameNode, index) => {
                const emojiNode = document.createElement('p');
                emojiNode.textContent = "Detected Mood: " + emojiEmotionMap[data2[index].detected_mood];
                emojiNode.style.marginLeft = '5px';
                emojiNode.style.color = '#71767B';
                emojiNode.style.font = '15px';
                emojiNode.style.fontFamily = 'TwitterChirp, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
                emojiNode.dataId = "detected_mood"
                // console.log(userNameNode.lastChild)
                // console.log(userNameNode.lastChild.dataId, userNameNode.lastChild.dataId!="detected_mood")
                if(data2[index]["is_english"] && userNameNode.lastChild.dataId!="detected_mood"){
                    userNameNode.appendChild(emojiNode);
                }
            });
        })

    });
}

addEmojis()