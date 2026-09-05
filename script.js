// =====================================
// EMAIL ANALYSIS
// =====================================

const emailForm = document.getElementById("emailForm");

if (emailForm) {

    emailForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const sender =
            document.getElementById("sender").value.trim();

        const subject =
            document.getElementById("subject").value.trim();

        const body =
            document.getElementById("body").value.trim();

        const result =
            document.getElementById("result");

        const resultTitle =
            document.getElementById("resultTitle");

        const resultIcon =
            document.getElementById("resultIcon");

        const riskBar =
            document.getElementById("riskBar");

        const riskScore =
            document.getElementById("riskScore");

        const category =
            document.getElementById("category");

        const reasons =
            document.getElementById("reasons");

        const recommendation =
            document.getElementById("recommendation");


        result.classList.remove("hidden");

        resultTitle.innerText =
            "⏳ Analyzing Email...";

        resultIcon.innerText = "🤖";

        riskScore.innerText = "Analyzing...";

        riskBar.style.width = "10%";

        reasons.innerHTML = "";

        try {

            const response = await fetch(
                "/analyze_email",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        sender: sender,
                        subject: subject,
                        body: body
                    })
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Analysis failed"
                );

            }


            // Result title
            resultTitle.innerText =
                data.result;


            // Risk score
            riskScore.innerText =
                data.risk + "%";


            // Category
            category.innerText =
                data.category;


            // Risk bar
            setTimeout(function() {

                riskBar.style.width =
                    data.risk + "%";

            }, 100);


            // Icon
            if (data.risk >= 70) {

                resultIcon.innerText = "🚨";

            } else if (data.risk >= 40) {

                resultIcon.innerText = "⚠️";

            } else {

                resultIcon.innerText = "✅";

            }


            // Reasons
            reasons.innerHTML = "";

            data.reasons.forEach(function(reason) {

                const li =
                    document.createElement("li");

                li.innerText = reason;

                reasons.appendChild(li);

            });


            // Recommendation
            recommendation.innerText =
                data.recommendation;


        } catch (error) {

            resultTitle.innerText =
                "❌ Error";

            resultIcon.innerText =
                "⚠️";

            riskScore.innerText =
                "N/A";

            recommendation.innerText =
                error.message;

        }

    });

}


// =====================================
// CLEAR HISTORY
// =====================================

async function clearHistory() {

    const confirmed =
        confirm(
            "Clear all analysis history?"
        );

    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/clear_history",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (data.success) {

            location.reload();

        }

    } catch (error) {

        alert(
            "Unable to clear history."
        );

    }

}


// =====================================
// LANGUAGE TOGGLE
// =====================================

const languageBtn =
    document.getElementById("languageBtn");


if (languageBtn) {

    let tamil = false;


    languageBtn.addEventListener(
        "click",
        function() {

            tamil = !tamil;


            if (tamil) {

                languageBtn.innerText =
                    "English";


                const heroText =
                    document.getElementById(
                        "heroText"
                    );


                if (heroText) {

                    heroText.innerText =
                        "சந்தேகமான மின்னஞ்சல்கள், மோசடிகள் மற்றும் phishing முயற்சிகளை கண்டறிய MailGuard AI உதவுகிறது.";

                }

            } else {

                languageBtn.innerText =
                    "தமிழ்";


                const heroText =
                    document.getElementById(
                        "heroText"
                    );


                if (heroText) {

                    heroText.innerText =
                        "Protect yourself from suspicious emails, scams and phishing attempts using intelligent email threat analysis.";

                }

            }

        }
    );

}
