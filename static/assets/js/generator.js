document.addEventListener("DOMContentLoaded", function () {
    console.log("Generator JS loaded.");

    const imageInput = document.getElementById("id_images");
    const analyzeForm = document.getElementById("analyze-form");
    const generateForm = document.getElementById("generate-form");

    const copyTitleBtn = document.getElementById("copy-title-btn");
    const copyListingBtn = document.getElementById("copy-listing-btn");

    const allowedMimeTypes = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/heic",
        "image/heif",
    ];

    const allowedExtensions = [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"];
    const maxFiles = 10;

    let feedbackBox = document.getElementById("upload-feedback");
    let previewBox = document.getElementById("image-preview");
    let loadingBox = document.getElementById("form-status");

    if (!feedbackBox && imageInput) {
        feedbackBox = document.createElement("div");
        feedbackBox.id = "upload-feedback";
        feedbackBox.className = "upload-feedback";
        imageInput.insertAdjacentElement("afterend", feedbackBox);
    }

    if (!previewBox && feedbackBox) {
        previewBox = document.createElement("div");
        previewBox.id = "image-preview";
        previewBox.className = "image-preview-grid";
        feedbackBox.insertAdjacentElement("afterend", previewBox);
    }

    if (!loadingBox) {
        loadingBox = document.createElement("div");
        loadingBox.id = "form-status";
        loadingBox.className = "form-status";
        loadingBox.style.display = "none";
        document.body.appendChild(loadingBox);
    }

    function clearFeedback() {
        if (!feedbackBox) return;
        feedbackBox.innerHTML = "";
        feedbackBox.className = "upload-feedback";
    }

    function setFeedback(message, type = "info") {
        if (!feedbackBox) return;
        feedbackBox.innerHTML = message;
        feedbackBox.className = `upload-feedback upload-feedback--${type}`;
    }

    function clearPreview() {
        if (!previewBox) return;
        previewBox.innerHTML = "";
    }

    function showStatus(message, type = "loading") {
        if (!loadingBox) return;
        loadingBox.textContent = message;
        loadingBox.className = `form-status form-status--${type}`;
        loadingBox.style.display = "block";
    }

    function hideStatus() {
        if (!loadingBox) return;
        loadingBox.textContent = "";
        loadingBox.className = "form-status";
        loadingBox.style.display = "none";
    }

    function getFileExtension(fileName) {
        const lastDot = fileName.lastIndexOf(".");
        if (lastDot === -1) return "";
        return fileName.slice(lastDot).toLowerCase();
    }

    function isAllowedFile(file) {
        const mimeType = (file.type || "").toLowerCase();
        const extension = getFileExtension(file.name || "");

        return allowedMimeTypes.includes(mimeType) || allowedExtensions.includes(extension);
    }

    function validateFiles(files) {
        const errors = [];
        const validFiles = [];

        if (!files || files.length === 0) {
            return { validFiles, errors };
        }

        if (files.length > maxFiles) {
            errors.push(`Max number of images reached. You can upload up to ${maxFiles} images.`);
        }

        Array.from(files).forEach((file) => {
            if (!isAllowedFile(file)) {
                errors.push(
                    `${file.name} has an unsupported format. Allowed formats: JPG, PNG, WEBP, HEIC.`
                );
                return;
            }

            validFiles.push(file);
        });

        return { validFiles, errors };
    }

    function createPreview(file, index) {
        if (!previewBox) return;

        const card = document.createElement("div");
        card.className = "image-preview-card";

        const image = document.createElement("img");
        image.className = "image-preview-card__image";
        image.alt = `Preview ${index + 1}`;

        const meta = document.createElement("div");
        meta.className = "image-preview-card__caption";
        meta.textContent = file.name;

        card.appendChild(image);
        card.appendChild(meta);
        previewBox.appendChild(card);

        const extension = getFileExtension(file.name || "");
        const mimeType = (file.type || "").toLowerCase();

        const isHeicLike =
            mimeType === "image/heic" ||
            mimeType === "image/heif" ||
            extension === ".heic" ||
            extension === ".heif";

        if (isHeicLike) {
            image.alt = `HEIC preview ${index + 1}`;
            image.style.display = "none";

            const placeholder = document.createElement("div");
            placeholder.className = "image-preview-card__placeholder";
            placeholder.textContent = "HEIC preview unavailable in browser";
            card.insertBefore(placeholder, meta);

            return;
        }

        const reader = new FileReader();

        reader.onload = function (e) {
            image.src = e.target.result;
        };

        reader.onerror = function () {
            image.remove();

            const placeholder = document.createElement("div");
            placeholder.className = "image-preview-card__placeholder";
            placeholder.textContent = "Preview unavailable";
            card.insertBefore(placeholder, meta);
        };

        reader.readAsDataURL(file);
    }

    function getTextContent(id) {
        const element = document.getElementById(id);
        return element ? element.innerText.trim() : "";
    }

    function getListingText() {
        const title = getTextContent("listing-title");
        const description = getTextContent("listing-description");
        const bullets = getTextContent("listing-bullets");
        const tags = getTextContent("listing-tags");

        return `${title}\n\n${description}\n\nBullet Points:\n${bullets}\n\nTags:\n${tags}`.trim();
    }

    async function copyToClipboard(text, successMessage, emptyMessage) {
        if (!text || !text.trim()) {
            alert(emptyMessage);
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            alert(successMessage);
        } catch (error) {
            console.error("Copy failed:", error);
            alert("Could not copy to clipboard.");
        }
    }

    if (imageInput) {
        imageInput.addEventListener("change", function () {
            hideStatus();
            clearFeedback();
            clearPreview();

            const files = this.files;
            const { validFiles, errors } = validateFiles(files);

            if (errors.length > 0) {
                setFeedback(errors.join("<br>"), "error");
                this.value = "";
                return;
            }

            if (validFiles.length === 0) {
                setFeedback("No images selected.", "info");
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
    }

    if (analyzeForm && imageInput) {
        analyzeForm.addEventListener("submit", function (e) {
            const files = imageInput.files;

            hideStatus();
            clearFeedback();

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

            showStatus(
                "Analyzing images... AI is checking details across all uploaded photos.",
                "loading"
            );
        });
    }

    if (generateForm) {
        generateForm.addEventListener("submit", function () {
            hideStatus();
            showStatus(
                "Generating listing... Preparing your title, description, tags and price ideas.",
                "loading"
            );
        });
    }

    if (copyTitleBtn) {
        copyTitleBtn.addEventListener("click", function () {
            const title = getTextContent("listing-title");
            copyToClipboard(title, "Title copied.", "No title to copy yet.");
        });
    }

    if (copyListingBtn) {
        copyListingBtn.addEventListener("click", function () {
            const listingText = getListingText();
            copyToClipboard(listingText, "Listing copied.", "No listing content to copy yet.");
        });
    }
});