document.addEventListener("DOMContentLoaded", function () {
    console.log("Generator JS loaded.");

    const imageInput = document.querySelector('input[name="images"]');
    const analyzeForm = document.querySelector('form button[name="analyze_image"]')?.closest("form");
    const generateForm = document.querySelector('form button:not([name="analyze_image"])')?.closest("form");

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    const maxFiles = 10;

    if (!imageInput) {
        return;
    }

    let feedbackBox = document.getElementById("upload-feedback");
    let previewBox = document.getElementById("image-preview");
    let loadingBox = document.getElementById("form-status");

    if (!feedbackBox) {
        feedbackBox = document.createElement("div");
        feedbackBox.id = "upload-feedback";
        feedbackBox.className = "upload-feedback";
        imageInput.insertAdjacentElement("afterend", feedbackBox);
    }

    if (!previewBox) {
        previewBox = document.createElement("div");
        previewBox.id = "image-preview";
        previewBox.className = "image-preview-grid";
        feedbackBox.insertAdjacentElement("afterend", previewBox);
    }

    if (!loadingBox) {
        loadingBox = document.createElement("div");
        loadingBox.id = "form-status";
        loadingBox.className = "form-status";
        document.body.appendChild(loadingBox);
    }

    function clearFeedback() {
        feedbackBox.innerHTML = "";
        feedbackBox.className = "upload-feedback";
    }

    function setFeedback(message, type = "info") {
        feedbackBox.innerHTML = message;
        feedbackBox.className = `upload-feedback upload-feedback--${type}`;
    }

    function clearPreview() {
        previewBox.innerHTML = "";
    }

    function createPreview(file, index) {
        const reader = new FileReader();

        const card = document.createElement("div");
        card.className = "image-preview-card";

        const image = document.createElement("img");
        image.className = "image-preview-card__img";
        image.alt = `Preview ${index + 1}`;

        const meta = document.createElement("div");
        meta.className = "image-preview-card__meta";
        meta.textContent = file.name;

        card.appendChild(image);
        card.appendChild(meta);
        previewBox.appendChild(card);

        reader.onload = function (e) {
            image.src = e.target.result;
        };

        reader.readAsDataURL(file);
    }

    function validateFiles(files) {
        const errors = [];
        const validFiles = [];

        if (files.length === 0) {
            return { validFiles, errors };
        }

        if (files.length > maxFiles) {
            errors.push(`Max number of images reached. You can upload up to ${maxFiles} images.`);
        }

        Array.from(files).forEach((file) => {
            if (!allowedTypes.includes(file.type)) {
                errors.push(
                    `${file.name} has an unsupported format. Allowed formats: JPG, PNG, WEBP, HEIC.`
                );
                return;
            }

            validFiles.push(file);
        });

        return { validFiles, errors };
    }

    imageInput.addEventListener("change", function () {
        clearFeedback();
        clearPreview();

        const files = this.files;
        const { validFiles, errors } = validateFiles(files);

        if (errors.length > 0) {
            setFeedback(errors.join("<br>"), "error");
            this.value = "";
            return;
        }

        if (validFiles.length === maxFiles) {
            setFeedback(
                `Max number of images reached: ${maxFiles}/${maxFiles}. You can now start analysis.`,
                "success"
            );
        } else {
            setFeedback(
                `${validFiles.length} image(s) selected. Allowed formats: JPG, PNG, WEBP, HEIC. Maximum: ${maxFiles}.`,
                "info"
            );
        }

        validFiles.forEach((file, index) => {
            createPreview(file, index);
        });
    });

    function showStatus(message, type = "loading") {
        loadingBox.textContent = message;
        loadingBox.className = `form-status form-status--${type}`;
        loadingBox.style.display = "block";
    }

    if (analyzeForm) {
        analyzeForm.addEventListener("submit", function (e) {
            const files = imageInput.files;

            if (!files || files.length === 0) {
                e.preventDefault();
                setFeedback("Please add at least 1 image before analysis.", "error");
                return;
            }

            const { errors } = validateFiles(files);

            if (errors.length > 0) {
                e.preventDefault();
                setFeedback(errors.join("<br>"), "error");
                return;
            }

            showStatus("Analyzing images... AI is checking details across all uploaded photos.", "loading");
        });
    }

    if (generateForm) {
        generateForm.addEventListener("submit", function () {
            showStatus("Generating listing... Preparing your title, description, tags and price ideas.", "loading");
        });
    }
});