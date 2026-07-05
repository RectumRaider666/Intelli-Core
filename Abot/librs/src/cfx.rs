use clap::Parser;
use playwright::Playwright;
use shared_memory::{ShmemConf, Shmem};
use tokio::time::{sleep, Duration};

#[derive(Parser)]
struct Args {
    #[arg(long)]
    shm_name: String,
    #[arg(long, default_value_t = false)]
    headless: bool,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let shmem = ShmemConf::new()
        .os_id(&args.shm_name)
        .size(8)
        .create()?;
    let playwright = Playwright::initialize().await?;
    let chromium = playwright.chromium()?;
    let browser = chromium
        .launcher()
        .headless(args.headless)
        .launch()
        .await?;
    let context = browser.new_context_builder().build().await?;
    let page = context.new_page().await?;
    page.goto_builder("https://cfbenchmarks.com/data/assets/BTC")
        .goto()
        .await?;
    let pointer = r#"/html/body/div/div/main/h1/div[4]/div/span[1]/span"#;
    let locator = page
        .locator_builder(format!("xpath={}", pointer))
        .build();
    locator.wait_for_builder().wait_for().await?;
    loop {
        if let Some(raw) = locator.text_content().await? {
            if raw != "-" {
                let cleaned = raw.replace('$', "").replace(',', "");
                if let Ok(price) = cleaned.parse::<f64>() {
                    let bytes = price.to_le_bytes();
                    unsafe {
                        let buf = shmem.as_slice_mut();
                        buf.copy_from_slice(&bytes);
                    }
                }
            }
        }
        sleep(Duration::from_secs(1)).await;
    }
}
