document.addEventListener('DOMContentLoaded', function() {
    // --- File Converter Tabs ---
    const tabPdf = document.getElementById('tab-pdf-to-word');
    const tabWord = document.getElementById('tab-word-to-pdf');
    const tabImage = document.getElementById('tab-image-to-pdf');
    const tabCsv = document.getElementById('tab-csv-to-pdf');
    const contentPdf = document.getElementById('content-pdf-to-word');
    const contentWord = document.getElementById('content-word-to-pdf');
    const contentImage = document.getElementById('content-image-to-pdf');
    const contentCsv = document.getElementById('content-csv-to-pdf');

    if (tabPdf && tabWord && tabImage && tabCsv && contentPdf && contentWord && contentImage && contentCsv) {
        tabPdf.addEventListener('click', function() {
            setActiveTab(tabPdf, [tabWord, tabImage, tabCsv]);
            showContent(contentPdf, [contentWord, contentImage, contentCsv]);
        });
        tabWord.addEventListener('click', function() {
            setActiveTab(tabWord, [tabPdf, tabImage, tabCsv]);
            showContent(contentWord, [contentPdf, contentImage, contentCsv]);
        });
        tabImage.addEventListener('click', function() {
            setActiveTab(tabImage, [tabPdf, tabWord, tabCsv]);
            showContent(contentImage, [contentPdf, contentWord, contentCsv]);
        });
        tabCsv.addEventListener('click', function() {
            setActiveTab(tabCsv, [tabPdf, tabWord, tabImage]);
            showContent(contentCsv, [contentPdf, contentWord, contentImage]);
        });
    }

    // --- PDF Editor Tabs ---
    const tabSplit = document.getElementById('tab-split');
    const tabMerge = document.getElementById('tab-merge');
    const tabEncrypt = document.getElementById('tab-encrypt');
    const tabDecrypt = document.getElementById('tab-decrypt');
    const tabWatermark = document.getElementById('tab-watermark');
    const tabRotate = document.getElementById('tab-rotate');
    const contentSplit = document.getElementById('content-split');
    const contentMerge = document.getElementById('content-merge');
    const contentEncrypt = document.getElementById('content-encrypt');
    const contentDecrypt = document.getElementById('content-decrypt');
    const contentWatermark = document.getElementById('content-watermark');
    const contentRotate = document.getElementById('content-rotate');

    if (tabSplit && tabMerge && tabEncrypt && tabDecrypt && tabWatermark && tabRotate && contentSplit && contentMerge && contentEncrypt && contentDecrypt && contentWatermark && contentRotate) {
        tabSplit.addEventListener('click', function() {
            setActiveTab(tabSplit, [tabMerge, tabEncrypt, tabDecrypt, tabWatermark, tabRotate]);
            showContent(contentSplit, [contentMerge, contentEncrypt, contentDecrypt, contentWatermark, contentRotate]);
        });
        tabMerge.addEventListener('click', function() {
            setActiveTab(tabMerge, [tabSplit, tabEncrypt, tabDecrypt, tabWatermark, tabRotate]);
            showContent(contentMerge, [contentSplit, contentEncrypt, contentDecrypt, contentWatermark, contentRotate]);
        });
        tabEncrypt.addEventListener('click', function() {
            setActiveTab(tabEncrypt, [tabSplit, tabMerge, tabDecrypt, tabWatermark, tabRotate]);
            showContent(contentEncrypt, [contentSplit, contentMerge, contentDecrypt, contentWatermark, contentRotate]);
        });
        tabDecrypt.addEventListener('click', function() {
            setActiveTab(tabDecrypt, [tabSplit, tabMerge, tabEncrypt, tabWatermark, tabRotate]);
            showContent(contentDecrypt, [contentSplit, contentMerge, contentEncrypt, contentWatermark, contentRotate]);
        });
        tabWatermark.addEventListener('click', function() {
            setActiveTab(tabWatermark, [tabSplit, tabMerge, tabEncrypt, tabDecrypt, tabRotate]);
            showContent(contentWatermark, [contentSplit, contentMerge, contentEncrypt, contentDecrypt, contentRotate]);
        });
        tabRotate.addEventListener('click', function() {
            setActiveTab(tabRotate, [tabSplit, tabMerge, tabEncrypt, tabDecrypt, tabWatermark]);
            showContent(contentRotate, [contentSplit, contentMerge, contentEncrypt, contentDecrypt, contentWatermark]);
        });
    }

    function setActiveTab(activeTab, inactiveTabs) {
        activeTab.classList.add('active');
        inactiveTabs.forEach(tab => tab.classList.remove('active'));
    }

    function showContent(activeContent, inactiveContents) {
        activeContent.style.display = '';
        inactiveContents.forEach(content => content.style.display = 'none');
    }

    // GSAP animation for card
    if (typeof gsap !== 'undefined') {
        gsap.from('.card-glass', {
            y: 40,
            opacity: 0,
            duration: 1,
            ease: 'power3.out'
        });
    }
});
