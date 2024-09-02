import re
    
def parse_topics_to_dict(text):
    topics = {}
    lines = text.strip().split('\n')
    current_topic = None
    
    topic_pattern = re.compile(r'^\d+\.\s+(.*)$')
    sub_topic_pattern = re.compile(r'^\*\s+(.*)$')

    for line in lines:
        line = line.strip()
        if topic_pattern.match(line):
            current_topic = topic_pattern.match(line).group(1)
            topics[current_topic] = []
        elif sub_topic_pattern.match(line):
            sub_topic = sub_topic_pattern.match(line).group(1)
            if current_topic:
                topics[current_topic].append(sub_topic)
    
    print(topics)
    return topics
