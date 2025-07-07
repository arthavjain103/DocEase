document.addEventListener('DOMContentLoaded', function() {
    // --- File Converter Tabs ---
    const tabPdf = document.getElementById('tab-pdf-to-word');
    const tabWord = document.getElementById('tab-word-to-pdf');
    const tabImage = document.getElementById('tab-image-to-pdf');
    const contentPdf = document.getElementById('content-pdf-to-word');
    const contentWord = document.getElementById('content-word-to-pdf');
    const contentImage = document.getElementById('content-image-to-pdf');

    if (tabPdf && tabWord && tabImage && contentPdf && contentWord && contentImage) {
        tabPdf.addEventListener('click', function() {
            setActiveTab(tabPdf, [tabWord, tabImage]);
            showContent(contentPdf, [contentWord, contentImage]);
        });
        tabWord.addEventListener('click', function() {
            setActiveTab(tabWord, [tabPdf, tabImage]);
            showContent(contentWord, [contentPdf, contentImage]);
        });
        tabImage.addEventListener('click', function() {
            setActiveTab(tabImage, [tabPdf, tabWord]);
            showContent(contentImage, [contentPdf, contentWord]);
        });
    }

    // --- PDF Editor Tabs ---
    const tabSplit = document.getElementById('tab-split');
    const tabMerge = document.getElementById('tab-merge');
    const tabEncrypt = document.getElementById('tab-encrypt');
    const tabDecrypt = document.getElementById('tab-decrypt');
    const contentSplit = document.getElementById('content-split');
    const contentMerge = document.getElementById('content-merge');
    const contentEncrypt = document.getElementById('content-encrypt');
    const contentDecrypt = document.getElementById('content-decrypt');

    if (tabSplit && tabMerge && tabEncrypt && tabDecrypt && contentSplit && contentMerge && contentEncrypt && contentDecrypt) {
        tabSplit.addEventListener('click', function() {
            setActiveTab(tabSplit, [tabMerge, tabEncrypt, tabDecrypt]);
            showContent(contentSplit, [contentMerge, contentEncrypt, contentDecrypt]);
        });
        tabMerge.addEventListener('click', function() {
            setActiveTab(tabMerge, [tabSplit, tabEncrypt, tabDecrypt]);
            showContent(contentMerge, [contentSplit, contentEncrypt, contentDecrypt]);
        });
        tabEncrypt.addEventListener('click', function() {
            setActiveTab(tabEncrypt, [tabSplit, tabMerge, tabDecrypt]);
            showContent(contentEncrypt, [contentSplit, contentMerge, contentDecrypt]);
        });
        tabDecrypt.addEventListener('click', function() {
            setActiveTab(tabDecrypt, [tabSplit, tabMerge, tabEncrypt]);
            showContent(contentDecrypt, [contentSplit, contentMerge, contentEncrypt]);
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
