class AISecurity:
    """
    AI Security & Response Filtering System
    - AI को अनऑथराइज़्ड सवालों का जवाब देने से रोकता है
    """

    blocked_words = ["hacking", "illegal", "violence", "shutdown", "malware", "exploit"]

    def filter_response(self, response):
        """
        AI के जवाब में अनऑथराइज़्ड शब्द होने पर उसे रोकें।
        """
        for word in self.blocked_words:
            if word in response.lower():
                return "⚠️ Unauthorized Response Blocked"
        return response

# **Usage Example**
if __name__ == "__main__":
    ai_security = AISecurity()
    print(ai_security.filter_response("Hacking tutorials for beginners"))
    print(ai_security.filter_response("How does AI work?"))