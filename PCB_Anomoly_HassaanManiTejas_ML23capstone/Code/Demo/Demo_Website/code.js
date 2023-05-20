const POST_URL = "http://127.0.0.1:5000/api/find_defects";

pred_b64 = undefined;
diff_b64 = undefined;
pre_b64 = undefined;

async function disp_proc_img() {
    if (pred_b64 == undefined) {
        alert("No image processed yet!");
        return;
    }
    const img = document.getElementById("img_disp");
    img.src = pred_b64;
}

async function disp_diff_img() {
    if (diff_b64 == undefined) {
        alert("No image processed yet!");
        return;
    }
    const img = document.getElementById("img_disp");
    img.src = diff_b64;
}

async function disp_pre_img() {
    if (pre_b64 == undefined) {
        alert("No image processed yet!");
        return;
    }
    const img = document.getElementById("img_disp");
    img.src = pre_b64;
}

async function process_img() {
    const file_form = document.getElementById("file");
    const file = file_form.files[0];
    base_64_str = await convertBase64(file);

    // update display
    const img = document.getElementById("img_disp");
    img.src = URL.createObjectURL(file);

    // make API call
    const res = await fetch(POST_URL, {
        method: "POST",
        // Adding body or contents to send
        body: JSON.stringify({
            data: base_64_str,
            preprocess: !document.getElementById("deep_pcb_box").checked
        }),
        // Adding headers to the request
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });


    const json_out = await res.json();

    // update b64 vars for render
    pred_b64 = json_out["tag_header"] + json_out["pred"];
    diff_b64 = json_out["tag_header"] + json_out["diff"];
    pre_b64 = json_out["tag_header"] + json_out["pre"];

    alert("Done Processing Image");
}

const convertBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader();
        fileReader.readAsDataURL(file);

        fileReader.onload = () => {
            resolve(fileReader.result);
        };

        fileReader.onerror = (error) => {
            reject(error);
        };
    });
}; 
