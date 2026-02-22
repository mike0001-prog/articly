function toggleContent(bodyId, btnId, overlayId) {
            const articleBody = document.getElementById(bodyId);
            const seeMoreBtn = document.getElementById(btnId);
            const fadeOverlay = document.getElementById(overlayId);
            console.log(articleBody)
            if (articleBody.classList.contains('expanded')) {
                // Collapse
                articleBody.classList.remove('expanded');
                seeMoreBtn.classList.remove('expanded');
                seeMoreBtn.innerHTML = `
                    See More
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 16px; height: 16px;">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                    </svg>
                `;
                // Scroll back to post
                articleBody.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                // Expand
                articleBody.classList.add('expanded');
                seeMoreBtn.classList.add('expanded');
                seeMoreBtn.innerHTML = `
                    See Less
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 16px; height: 16px;">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                    </svg>
                `;
            }
        }
        
        // Auto-hide "See More" button for short content
        document.addEventListener('DOMContentLoaded', function() {
            // Check all article bodies
            // console.log("test")
            document.querySelectorAll('.article-text').forEach(function(articleBody) {
                // console.log(articleBody)
                const id = articleBody.id;
                const counter = id.replace('articleBody', '');
                const seeMoreContainer = document.getElementById('seeMoreContainer' + counter);
                const fadeOverlay = document.getElementById('fadeOverlay' + counter);
                
                // Check if content height exceeds max-height (200px)
                if (articleBody.scrollHeight <= 300) {
                    // Content is short, hide see more button and fade overlay
                    if (seeMoreContainer) {
                        seeMoreContainer.style.display = 'none';
                    }
                    if (fadeOverlay) {
                        fadeOverlay.style.display = 'none';
                    }
                }
            });
        });



