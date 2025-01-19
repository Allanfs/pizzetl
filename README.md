# Referências para cloud functions
Esse vídeo contem instruções para fazer deploy na function via Terraform.
Pelo que vi rapidamente, é possivel gerar nova versão de function:
- fazendo upload de arquivo .zip
- alterando diretamente no browser
- através de repositório no proprio GCP
- Talvez seja possível configurar cloud build para fazer a atualização

https://www.youtube.com/watch?v=LAcErtGU-VU&ab_channel=AntonPutra
https://cloud.google.com/storage/docs/uploading-objects?hl=pt-br#storage-upload-object-nodejs
https://cloud.google.com/storage/docs/uploading-objects-from-memory?hl=pt-br#storage-upload-object-from-memory-nodejs
https://github.com/adaltas/node-csv#readme

Definir variáveis de ambiente para a Cloud Function
---

https://cloud.google.com/functions/docs/configuring/env-var

Acessar Secret Manager
---

https://cloud.google.com/functions/docs/configuring/secrets#making_a_secret_accessible_to_a_function

Executar e testar cloud functions localmente
---

É possível testar para input de requisição HTTP, evento e cloudevent através da `FUNCTION_SIGNATURE_TYPE` (`--signature-type`)

https://www.npmjs.com/package/@google-cloud/functions-framework


# Python

- https://cloud.google.com/functions/docs/samples/functions-cloudevent-storage?hl=en
- https://cloud.google.com/functions/docs/running/function-frameworks#functions-local-ff-install-python
- https://cloud.google.com/bigquery/docs/samples/bigquery-pandas-gbq-to-gbq-simple
- https://github.com/GoogleCloudPlatform/functions-framework-python
- https://cloud.google.com/bigquery/docs/schemas#specify_schemas

## Testar local
```sh
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES functions-framework --target consolidar_plataformas
```

[Por que definir OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES](https://stackoverflow.com/a/52230415)


```sh
curl --location 'localhost:8080' \
--header 'Content-Type: application/cloudevents+json' \
--data '{
    "specversion": "1.0",
    "type": "example.com.cloud.event",
    "source": "https://example.com/cloudevents/pull",
    "subject": "123",
    "id": "A234-1234-1234",
    "time": "2018-04-05T17:31:00Z",
    "data": {
        "bucket": "bucket_teste",
        "name": "arquivo.csv"
    }
}'
```

## Testes unirários

```sh
python -m unittest discover
python -m unittest discover aplicativos
```


## Deploy
> DEPRECATED: Utilizar o deploy.sh

Fazer deploy com Terraform:
```sh
cd terraform
terraform apply
# yes
```