## Get the topic from the book
get_the_topics_template = """
**Tugas:** Analisis gambar yang diberikan, yang berisi daftar isi buku, dan ekstrak topik utama serta subtopiknya.

**Instruksi:**

1. **Topik Utama:** Identifikasi setiap topik utama dalam buku, kecuali bagian seperti latar belakang, kata pengantar, pendahuluan, dan referensi.

2. **Subtopik:** Untuk setiap topik utama, daftarkan subtopik yang sesuai.

**Format Output:**

1. **Topik Utama 1**
   * Subtopik 1
   * Subtopik 2
   etc

2. **Topik Utama 2**
   * Subtopik 1
   * Subtopik 2
   etc

etc

**Pedoman Penting:**

- Pastikan topik utama dan subtopik diidentifikasi dengan jelas dan dicantumkan dalam urutan yang tepat seperti yang muncul dalam gambar.
- Jangan sertakan informasi tambahan selain topik utama dan subtopik.
- Patuhi format yang diberikan.
"""

refined_get_topic_template = """
Ensure the following topic and subtopic are provided:

{topics}

Follow this format : 

1. **Topik Utama 1**
   * Subtopik 1
   * Subtopik 2
   * etc

2. **Topik Utama 2**
   * Subtopik 1
   * Subtopik 2
   * etc

etc

Do not add any additional text; only use the specified format.
"""

human_topic_explanation_template = """
Jelaskan secara ringkas dan padat tentang topik yang diberikan yaitu {{topic}}, dengan fokus pada poin-poin utama dan konsep kunci. Jelaskan dengan bahasa indonesia tanpa mengubah istilah kedokteran.Gambarkan materi ini secara jelas, seolah-olah menjelaskan kepada seseorang yang baru pertama kali belajar tentang topik ini.
"""

human_sub_topic_explanation_template = """
Jelaskan materi dari subtopik yang merupakan penjabaran dari topik utama yang diberikan. Materi yang diberikan berkaitan dengan kedokteran. Pastikan penjelasan tersebut komprehensif, jelas, dan relevan dengan topik dan subtopic yang diberikan. Jelaskan dengan bahasa indonesia tanpa mengubah istilah kedokteran.

berikut adalah subtopik dan topik utamanya : 

Subtopik: {{subtopic}}

Topik utama: {{topic}}

Format Output:

Berikan penjelasan yang komprehensif dan relevan mengenai subtopik {{subtopic}} dalam konteks topik utama {{topic}}. Pastikan penjabaran ini jelas, mendalam, dan sesuai dengan konteks kedokteran yang diberikan. Gunakan terminologi medis yang tepat dan contoh yang relevan jika diperlukan.
"""

system_summarize_template = """

"""
human_summarize_template = """
Please summarize the given context based on the specified instruction. Ensure that the summary is concise and captures the main points relevant to the instruction. The summary should be coherent and clear, presenting information in a straightforward manner. If the instruction requires a list format or specific details, include those as necessary to fulfill the instruction accurately.

Be careful to follow the additional instruction precisely.

Additional Instruction:
{additional_instruction}

Provide the summary using only the information from the given context.

Context:
{context}

If the context does not provide sufficient information to create a summary based on the instruction, do not provide any content.
"""


