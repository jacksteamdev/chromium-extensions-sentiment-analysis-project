# Developer Relations Report: January 2024

## Key Insights

1. **Increased Discussion on Manifest V3 Transition**: There's a noticeable increase in threads discussing the transition from Manifest V2 to Manifest V3, highlighting concerns about feature parity and implementation challenges. This transition is a significant focus for developers, with many seeking guidance on adapting their extensions.

2. **Concerns Over Chrome Web Store (CWS) Policies and Processes**: Several threads indicate ongoing concerns with CWS policies, particularly around extension reviews, search functionality, and analytics. Developers express frustration with perceived inconsistencies and lack of clarity in the review process, as well as difficulties in managing user feedback effectively.

3. **Technical Challenges and API Limitations**: Developers are actively discussing technical challenges related to Chrome Extension APIs, including issues with `declarativeNetRequest`, `chrome.scripting.executeScript`, and handling of CSP with content scripts. There's a strong desire for more robust documentation and examples to navigate these complexities.

4. **Community Engagement and Support**: The threads show a healthy level of community engagement, with developers offering support and sharing solutions to common problems. However, there's also a call for more direct support from the Chrome Extensions team, especially in addressing bugs and feature requests.

5. **Security and Privacy Concerns**: Security and privacy remain top concerns among developers, especially in light of new API restrictions and the push for more secure extension practices. Discussions around handling user data, permissions, and secure communication channels are prevalent.

## Top Posts

### Top 3 Negative Posts
1. **Memory Leak Issue**[^1]: Developers express frustration over a chronic memory leak issue when creating new tabs, highlighting the negative impact on performance and user experience.
2. **CWS Search Functionality**[^2]: Negative sentiment around the Chrome Web Store's search functionality, with developers frustrated by irrelevant search results and keyword spamming.
3. **Restrictions on Inline Script Execution**[^3]: Concerns about the limitations imposed by CSP on inline script execution in content scripts, with developers seeking more flexibility.

### Top 3 Unresolved Posts
1. **Extensions Deploying Scripts in DOM**[^4]: Ongoing discussion on the interaction of CSP with extensions trying to add inline code to the DOM, with no clear resolution.
2. **Problems with webRequest API**[^5]: Developers discuss challenges with the `webRequest` API in manifest v3, particularly the removal of `webRequestBlocking`, without a satisfactory resolution.
3. **Accessing DevTools Waterfall**[^6]: A developer seeks to access raw information from the DevTools "waterfall" UI, with no direct solution provided.

### Top 3 Positive Posts
1. **Documentation Relaunch**[^7]: Positive feedback on the relaunch of Chrome Extensions documentation, with developers appreciating the improved navigation and search experience.
2. **Handling Inline JavaScript in MV3**[^8]: A developer finds a solution to executing inline JavaScript in content scripts, sharing a positive outcome with the community.
3. **New Messaging Library: extension-bus**[^9]: A developer shares a new messaging library for Chrome and Firefox extensions, receiving positive feedback and constructive suggestions.

### Top 3 Resolved Posts
1. **Alarms API Issue**[^10]: A developer resolves an issue with the Chrome Alarms API not working properly after installing an extension from the CWS.
2. **Publishing React Chrome Extension**[^11]: A developer successfully resolves a review process issue with their React-based Chrome extension.
3. **Spam in Forum**[^12]: The issue of spam in the Chromium Extensions Google Group was resolved with stricter automation and collaboration with the spam detection team.

[^1]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/59068c6b-7757-4451-a1fa-35d9b658b6e5n%40chromium.org
[^2]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/c79f66c6-3861-4f0f-9d63-f5b2eb175027n%40chromium.org
[^3]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/b0c01d7c-30a7-4b68-ad8d-25930a8c0adcn%40chromium.org
[^4]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/231120bd-1202-448f-9363-7f35ec789cdfn%40chromium.org
[^5]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/693509af-b93b-4ece-aa09-aac21889f2b5n%40chromium.org
[^6]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/fe8cbc4d-6dcd-4f88-b5f8-b3eedfec9416n%40chromium.org
[^7]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/b77042c6-2662-40af-b3e2-cb809fb1249fn%40chromium.org
[^8]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/e0330a17-cf30-42c7-897c-68a4e5a48e1an%40chromium.org
[^9]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/0acf3925-70fe-4e81-87da-786d18ad6c61n%40chromium.org
[^10]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/f649568e-7461-4328-b1c6-88609ed40f35n%40chromium.org
[^11]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/cb255fd0-8032-47f6-a7ed-9caf5e61bb5an%40chromium.org
[^12]: https://groups.google.com/a/chromium.org/d/msgid/chromium-extensions/CAAgdh1JYHO2ZUbFsGcmo1Rxx%2BztxSUVV_DW4JWeddpEx-Zb5NA%40mail.gmail.com