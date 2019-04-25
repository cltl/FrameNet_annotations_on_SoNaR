



class Frame:
    """
    instance of a frame
    """
    def __init__(self, doc_name, m_id, tokens):
        self.doc_name = doc_name
        self.m_id = m_id
        self.id_ = (self.doc_name, self.m_id)
        self.tokens = tokens
        self.frame = set()
        self.confidence_frame = []
        self.roles = dict()

    def __str__(self):
        info = [f'ID: {self.doc_name} {self.m_id}']
        info.append(' '.join(token['text']
                            for token in self.tokens))
        info.append(f'frame: {self.frame}')
        info.append(f'confidence frame: {self.confidence_frame}')
        for role, role_info in self.roles.items():
            info.append(f'ROLE (m_id -> {role_info.m_id}): {role} (confidence: {role_info.confidence_role})')
            text = ' '.join(token['text']
                            for token in role_info.tokens)
            info.append(f'ROLE TEXT: {text}\n')

        return '\n'.join(info)


class FrameElement:
    """
    instance of a frame element
    """
    def __init__(self, doc_name, m_id, tokens):
        self.doc_name = doc_name
        self.m_id = m_id
        self.tokens = tokens
        self.confidence_role = None


    def __str__(self):
        info = [f'ID: {self.doc_name} {self.m_id}']
        info.append()

        return '\n'.join(info)

