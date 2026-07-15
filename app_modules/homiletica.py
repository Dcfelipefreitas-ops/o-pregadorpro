import re

class PastoralReviewer:
    """Analisador de Qualidade e Ortografia para Mensagens."""
    
    PALAVRAS_CHAVE_TEOLOGICAS = ["exegese", "hermenêutica", "escatologia", "soteriologia", "cristocentrismo"]

    @staticmethod
    def checar_ortografia_basica(texto):
        """Analisa vícios de linguagem e pontuação."""
        alertas = []
        if len(texto) < 100:
            alertas.append("⚠️ Conteúdo muito curto para um esboço profundo.")
        
        # Procura por parágrafos muito longos (falta de pausas para o ouvinte)
        paragrafos = texto.split('\n')
        for p in paragrafos:
            if len(p) > 300:
                alertas.append("🔍 Parágrafo denso detectado. Considere quebras para melhorar a oratória.")
        
        return alertas

    @staticmethod
    def analisar_densidade_teologica(texto):
        """Verifica se o vocabulário está rico para o gabinete pastoral."""
        encontradas = [w for w in PastoralReviewer.PALAVRAS_CHAVE_TEOLOGICAS if w in texto.lower()]
        return len(encontradas)
