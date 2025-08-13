# marketup-tweaks

Scripts Python que tentam contornar algumas limitações práticas do ERP MarketUP:

  - Exportação em massa de todas as movimentações de estoque de um determinado período para controle de lote e datas de fabricação e validade;
  - Automatização de exportação e download de arquivos .xml de notas fiscais emitidas (o sistema só guada 15 dias de histórico em sua versão paga, e você precisa exportar os arquivos para guarda-los pelo tempo exigido pela legislação).

__UTILIZAÇÃO__

  Preencha o arquivo ___auth\auth.txt___ com o seu bearer token (primeira linha) e seu x-auth token (segunda linha). Não utlize aspas ou espaços, apenas os caracteres dos tokens, um por linha. Para obter os tokens você precisará inspecionar uma sessão logada no MarketUP e copia-los do cabeçalho de uma solicitação qualquer. Estes tokens mudam de tempos em tempos, por isso há um arquivo separado para facilitar a execução dos scripts.

  Em cada um dos scripts, altere a propriedade "Referer" para que fique com a sua URL pública no MerketUP (esta informação não muda, você só precisará editá-la uma vez).

  Altere as datas de início e fim das solicitações, diretamente nos scripts.

Após isso, basta rodar os scripts.

  __lote_validade.py__ - irá criar um arquivo .csv com todas as movimentações do período solicitado, incluindo: nome do produto, código de barras, data de fabricação, data de validade e número de lote. Muito útil para comércios que precisam controlar lote e validade de produtos.

  __export_xml.py__ - irá incluir no sistema uma tarefa de exportação de arquivos .xml do período solicitado, e irá validar, de 10 em 10 segundos, se a tarefa foi concuída. Caso positivo, irá realizar o download do aquivo .zip automaticamente no mesmo diretório do script.

  __Observação__: não altere a estrutura de diretórios. Caso altere, será necessário modificar a sessão ___CONFIGURAÇÕES___ dos scripts para garantir que seja possível ler os tokens de autenticação.
