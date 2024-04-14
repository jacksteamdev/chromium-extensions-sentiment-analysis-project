# Developer Relations Report: March 2024

## Key Insights

1. **Increased Concerns Over Extension Reviews**: There has been a notable increase in threads related to the Chrome Web Store, particularly concerning the review process for extensions and the handling of spam reviews. Developers express frustration over delays and lack of transparency, impacting their extension's visibility and user trust.

2. **Technical Challenges with Manifest V3**: Developers continue to face challenges adapting to Manifest V3, especially regarding service workers and background scripts. Issues like message passing between different parts of the extension (e.g., service workers to side panels) and limitations with current APIs are common. Despite these challenges, there's a positive sentiment towards finding workarounds and solutions within the community.

3. **Need for Better Documentation and Examples**: Several threads highlight a need for more comprehensive documentation and real-world examples, especially for newer or less-documented features like DNS prefetching in side panels and handling tab groups. Developers seek more guidance on best practices and efficient implementation strategies.

## Top Posts

### Top 3 Negative Posts

1. **Bombarded with Spam Reviews**[^1]: Developers report significant issues with spam reviews on the Chrome Web Store, affecting their ratings and potentially their livelihood. The thread reflects deep frustration with the review system's slow response to fake, damaging reviews.

2. **Service Worker code paused when popup is closed in MV3**[^2]: This thread discusses a developer's struggle with service worker scripts pausing unexpectedly in Manifest V3, highlighting the technical challenges and limitations developers face with the new manifest version.

3. **Extension Disabled on Chrome restart**[^3]: A developer reports their extension being unexpectedly disabled after Chrome restarts, causing confusion and concern over potential impacts on user experience and extension reliability.

### Top 3 Unresolved Posts

1. **Chrome Extension API - Unable to update saved tab groups in Chrome**[^4]: Developers express disappointment over the inability to update saved tab groups, impacting the functionality of their extensions.

2. **Extension id - enhpjjojmnlnaokmppkkifgaonfojigl - pending review**[^5]: A developer seeks help for an extension stuck in review, highlighting the challenges and uncertainties of the Chrome Web Store's review process.

3. **background/servicework sendMessage() to sidepanel's iframe**[^6]: A technical discussion on messaging challenges between service workers and iframes in side panels, with no clear resolution provided.

### Top 3 Positive Posts

1. **Extension not working when chrome://flags/#test-third-party-cookie-phaseout is enabled**[^7]: A developer successfully resolves an issue with their extension failing due to third-party cookie phaseout, showcasing effective problem-solving and community support.

2. **Accidentally Took Extension off Store**[^8]: A developer accidentally unpublishes their extension but receives prompt and helpful support, leading to a positive resolution.

3. **Display all Reviews on new Webstore**[^9]: Developers appreciate the new Chrome Web Store feature allowing them to view reviews in all languages, improving their ability to engage with user feedback.

### Top 3 Resolved Posts

1. **Extension should work on specific sites only**[^10]: A developer seeks guidance on activating their extension only on specified websites, and the issue is resolved with the suggestion to use runtime permission requests.

2. **Extension installed via Google Cloud is disabled in Chrome version 123**[^11]: A self-hosted extension gets disabled in Chrome version 123, but the Chromium team acknowledges the issue and works on a fix.

3. **banana constructor of banana-i18n not being recognized inside service worker in manifest V3**[^12]: Developers discuss transitioning from manifest V2 to V3, focusing on communication between service workers and content scripts. The thread provides solutions to the initial problem, reflecting a collaborative effort to overcome technical challenges.

[^1]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/ea5414dd-5372-4fb3-9b20-eb2abb5ecf2dn%40chromium.org
[^2]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/1e37b38f-0898-428a-af26-34b17d1220dbn%40chromium.org
[^3]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/c79fd09f-fa0a-4df6-820b-acbab988c92fn%40chromium.org
[^4]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/CAPiq7peSk%3DcCqZ_b5Xo4wHGvKuOWOxC6YFqwcZz%2BnB-cs6SZWg%40mail.gmail.com
[^5]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/816a22eb-cc74-457f-a09f-d915143e5a44n%40chromium.org
[^6]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/01473eca-59a6-4a52-b90c-e2a743d86f41n%40chromium.org
[^7]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/5aa79165-5482-4179-847a-f95c8e69bc9dn%40chromium.org
[^8]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/279d003b-ad98-4114-841a-3013aef1f8bdn%40chromium.org
[^9]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/8ab88de3-c48f-4fa1-9777-4226236f75ben%40chromium.org
[^10]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/2e1303b2-ab0e-462b-a506-d326dd0ec02cn%40chromium.org
[^11]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/57121fcf-ab22-4b1e-ba58-c1a01cbe08a9n%40chromium.org
[^12]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/86c98a6e-41e9-41a3-a3cd-3f6ecfd11aa4n%40chromium.org