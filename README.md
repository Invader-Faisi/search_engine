Keyword-Based Search Engine for Text Documents

Project Domain / Category
Information Retrieval

Abstract / Introduction
In today's information-driven world, individuals and organizations generate and store an enormous amount of textual data across various platforms. The ability to efficiently retrieve relevant information from this vast pool is crucial for productivity and decision-making. This project aims to develop a Keyword-Based Search Engine for Text Documents, providing a streamlined solution for users to quickly locate specific information within their documents. By offering an intuitive web interface, the search engine empowers users to input keywords and phrases to receive immediate, relevant search results. The system prioritizes the most pertinent documents, ensuring users find what they need swiftly and effectively. This project addresses the increasing demand for efficient information retrieval systems, ultimately enhancing document management processes and boosting overall efficiency.
Functional Requirements

1. User Interface:
   a) A clean and intuitive web-based interface that allows users to interact with the search engine seamlessly.
   b) The main page should include:
   i) A prominently displayed search bar for keyword and phrase input.
   ii) Clear instructions or placeholder text to guide users in entering their search terms.
   iii) A section displaying search results in a well-organized manner, allowing easy navigation.
   iv) Responsive design for compatibility across different devices (desktops, tablets, smartphones).
   v) Option to view details of each document directly from the search results.

2. Document Uploading:
   a) Users can upload multiple text documents (e.g., .txt, .csv) via a file input interface.
   b) Provide feedback upon successful document upload, indicating the number of documents uploaded.
   c) Users must create an account and login first to upload text documents. The account will require basic information such as username, password, and email address.

3. Keyword and Phrase Search Functionality with Spell Checker:
   a) Users can enter keywords and phrases in a search box to retrieve relevant documents.
   b) The system processes the input keywords and phrases, matching them against the content of the uploaded documents.
   c) As users type keywords or phrases, the system automatically checks for spelling errors in real-time, underlining misspelled words with a red wavy line.
   d) When users right-click a misspelled word, the system provides spelling suggestions.
   e) When hovering over a misspelled word, the system displays the correct spellings as a tooltip.
   f) Allow users to add custom words to their dictionary if they frequently use specialized terms.
   g) Display the most relevant document first, followed by subsequent results ranked by relevance, along with the occurrences of the keywords or phrases within those documents.
   h) A user does not need any account or login for using search functionality, viewing and downloading documents.

4. Search Results Display:
   a) Present the search results in a user-friendly format, showing:
   i) Document name
   ii) Snippet of text containing the keyword(s) or phrase(s)
   iii) Option to view or download the document.
   b) Highlight the keywords and phrases within the snippets to enhance visibility.

5. Document Indexing:
   a) Automatically index the contents of uploaded text documents to optimize search performance.
   b) Store relevant metadata for each document, including:
   i) Document name
   ii) Upload date
   iii) Username (who uploaded the document)
   iv) Keywords and phrases extracted from the content.
   c) Implement efficient indexing algorithms to improve search speed and accuracy, considering both keyword and phrase indexing.

6. User Notifications:
   a) Display success messages upon successful upload of documents.
   b) Provide feedback for potential issues, such as no documents uploaded, to guide user actions.

7. Accessibility Features:
   a) Ensure the web interface is accessible to all users, including those with disabilities (e.g., using proper HTML semantic elements, keyboard navigation).

8. Data Persistence
   a) Efficient Storage: Use SQLite for metadata and store documents in a dedicated directory.
   b) Indexing: Implement Whoosh to index document content for fast searches.
   c) Optimization: Optimize SQL queries and utilize caching to enhance performance.
   d) Data Integrity: Ensure data consistency through transactions and robust error handling.
   e) Session Management: Track user interactions and maintain a history of recently accessed documents.
   f) Backups: Schedule regular backups for data recovery.
   g) Scalability: Design for future growth in document volume and user access.
9. Admin Management: There should be an Admin account to manage user accounts, including adding, modifying, or deleting user accounts and monitoring user activities.
   Tools:

1) Python: The primary programming language for backend development, document processing, and implementing search algorithms.
2) Flask: A python web framework for building the web interface and handling user requests.
3) SQLite: The database for storing uploaded documents and indexed data.
4) Whoosh: A python search library for indexing and searching functionalities.
5) HTML/CSS: For structuring and styling the web interface.
6) JavaScript: For client-side interactivity and enhancing user experience.
